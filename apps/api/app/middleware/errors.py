import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.log_context.context import get_correlation_id, set_trace_id
from app.telemetry.tracing import current_trace_id

logger = logging.getLogger("opsight.errors")


class DependencyFailure(RuntimeError):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DependencyFailure)
    async def dependency_failure_handler(request: Request, exc: DependencyFailure):
        set_trace_id(current_trace_id())
        logger.exception("dependency failure", extra={"path": request.url.path, "status_code": 503})
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": "dependency_unavailable", "message": str(exc), "correlation_id": get_correlation_id()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        set_trace_id(current_trace_id())
        logger.exception("unhandled exception", extra={"path": request.url.path, "status_code": 500})
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "internal_server_error",
                "message": "Unexpected service failure",
                "correlation_id": get_correlation_id(),
            },
        )
