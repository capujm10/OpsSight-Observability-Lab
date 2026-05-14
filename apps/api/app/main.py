from app.api import health, orders, simulate
from app.config.settings import get_settings
from app.log_context.json_logger import configure_logging
from app.middleware.correlation import CorrelationAndMetricsMiddleware
from app.middleware.errors import register_exception_handlers
from app.telemetry.metrics import metrics_response
from app.telemetry.tracing import configure_tracing
from fastapi import FastAPI

settings = get_settings()
configure_logging(settings)

app = FastAPI(
    title="OpsSight Observability Lab API",
    version=settings.service_version,
    description="Production-style API used to exercise metrics, logs, traces, alerts, and incident workflows.",
)
app.add_middleware(CorrelationAndMetricsMiddleware)
register_exception_handlers(app)
configure_tracing(app, settings)

app.include_router(health.router)
app.include_router(orders.router)
app.include_router(simulate.router)


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return metrics_response()
