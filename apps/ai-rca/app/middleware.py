import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.request_context import correlation_id_ctx, trace_id_ctx
from app.telemetry.metrics import AI_RCA_ACTIVE_REQUESTS
from app.telemetry.tracing import current_trace_id

logger = logging.getLogger("ai-rca.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id_ctx.set(request.headers.get("x-correlation-id", str(uuid4())))
        started = time.perf_counter()
        AI_RCA_ACTIVE_REQUESTS.inc()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            AI_RCA_ACTIVE_REQUESTS.dec()
            trace_id_ctx.set(current_trace_id())
            logger.info(
                "ai rca request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": getattr(response, "status_code", 500),
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
