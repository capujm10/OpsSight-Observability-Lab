import asyncio
import logging
import random
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.settings import get_settings
from app.logging_config import configure_logging
from app.logging_context import correlation_id_ctx, trace_id_ctx
from app.metrics import PAYMENT_ACTIVE_REQUESTS, PAYMENT_DURATION_SECONDS, PAYMENT_REQUESTS_TOTAL, metrics_response
from app.security import SecurityHeadersMiddleware
from app.tracing import configure_tracing, current_trace_id

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("payment-gateway")

app = FastAPI(title="OpsSight Payment Gateway", version=settings.service_version)
configure_tracing(app, settings)


class PaymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: str = "authorize"
    force_failure: bool = False
    latency_multiplier: float = Field(default=1.0, ge=0.1, le=10.0)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id_ctx.set(request.headers.get("x-correlation-id", str(uuid4())))
        started = time.perf_counter()
        PAYMENT_ACTIVE_REQUESTS.inc()
        try:
            response = await call_next(request)
            return response
        finally:
            PAYMENT_ACTIVE_REQUESTS.dec()
            trace_id_ctx.set(current_trace_id())
            logger.info(
                "dependency request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": getattr(locals().get("response", None), "status_code", 500),
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )


app.add_middleware(RequestContextMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/api/v1/payments/authorize")
async def authorize(payload: PaymentRequest):
    started = time.perf_counter()
    outcome = "success"
    status_code = 200
    latency = (settings.base_latency_ms / 1000) * max(payload.latency_multiplier, 0.1)
    await asyncio.sleep(latency + random.uniform(0.01, 0.06))
    if payload.force_failure or random.random() < settings.failure_rate:
        outcome = "failure"
        status_code = 503
    PAYMENT_DURATION_SECONDS.labels(operation=payload.operation, outcome=outcome).observe(time.perf_counter() - started)
    PAYMENT_REQUESTS_TOTAL.labels(operation=payload.operation, status_code=str(status_code), outcome=outcome).inc()
    logger.info("payment dependency operation", extra={"operation": payload.operation, "outcome": outcome, "status_code": status_code})
    if status_code >= 500:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "dependency": "payment-gateway", "operation": payload.operation, "outcome": outcome},
        )
    return {"status": "success", "dependency": "payment-gateway", "operation": payload.operation, "outcome": outcome}


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return metrics_response()
