import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.log_context.context import set_correlation_id, set_trace_id
from app.telemetry.metrics import HTTP_ACTIVE_REQUESTS, HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL
from app.telemetry.tracing import current_trace_id

logger = logging.getLogger("opsight.request")


class CorrelationAndMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
        set_correlation_id(correlation_id)
        method = request.method
        started = time.perf_counter()
        HTTP_ACTIVE_REQUESTS.labels(method=method, route=route_path).inc()
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - started
            trace_id = current_trace_id()
            set_trace_id(trace_id)
            status_code = locals().get("status_code", 500)
            HTTP_ACTIVE_REQUESTS.labels(method=method, route=route_path).dec()
            HTTP_REQUESTS_TOTAL.labels(method=method, route=route_path, status_code=str(status_code)).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, route=route_path).observe(duration)
            if "response" in locals():
                response.headers["x-correlation-id"] = correlation_id
                response.headers["x-trace-id"] = trace_id
            logger.info(
                "request completed",
                extra={
                    "method": method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "client_ip": request.client.host if request.client else "-",
                },
            )
