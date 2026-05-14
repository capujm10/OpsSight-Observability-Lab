from fastapi import FastAPI

from app.config import get_settings
from app.logging_config import configure_logging
from app.middleware import RequestContextMiddleware
from app.models.rca import AlertmanagerWebhook, IncidentContext, RCAResponse, WebhookRCAResult
from app.security import SecurityHeadersMiddleware
from app.telemetry.metrics import metrics_response
from app.telemetry.tracing import configure_tracing
from app.workflows.rca_workflow import RCAWorkflow

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="OpsSight AI RCA",
    version=settings.service_version,
    description=(
        "Local-first operational intelligence service for incident summarization, "
        "telemetry interpretation, RCA hypotheses, and remediation guidance."
    ),
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)
configure_tracing(app, settings)
workflow = RCAWorkflow(settings)


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready", "provider": settings.ai_provider}


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return metrics_response()


@app.post("/api/v1/rca/analyze", response_model=RCAResponse)
async def analyze(context: IncidentContext) -> RCAResponse:
    return await workflow.analyze(context, workflow="rca")


@app.post("/api/v1/alerts/explain", response_model=RCAResponse)
async def explain_alert(context: IncidentContext) -> RCAResponse:
    return await workflow.analyze(context, workflow="alert-explanation")


@app.post("/api/v1/traces/summarize", response_model=RCAResponse)
async def summarize_traces(context: IncidentContext) -> RCAResponse:
    return await workflow.analyze(context, workflow="trace-summary")


@app.post("/api/v1/logs/summarize", response_model=RCAResponse)
async def summarize_logs(context: IncidentContext) -> RCAResponse:
    return await workflow.analyze(context, workflow="log-summary")


@app.post("/api/v1/postmortems/enrich", response_model=RCAResponse)
async def enrich_postmortem(context: IncidentContext) -> RCAResponse:
    return await workflow.analyze(context, workflow="postmortem-enrichment")


@app.post("/api/v1/alertmanager/webhook", response_model=WebhookRCAResult)
async def alertmanager_webhook(payload: AlertmanagerWebhook) -> WebhookRCAResult:
    return await workflow.analyze_alertmanager_webhook(payload)
