import logging
import time

from app.config import Settings
from app.models.rca import AlertmanagerWebhook, IncidentContext, RCAResponse, WebhookRCAResult
from app.prompts import load_prompt
from app.providers import build_provider
from app.services.alertmanager import incident_from_alert
from app.services.artifact_store import RCAArtifactStore
from app.services.grafana_links import build_grafana_links
from app.services.live_enrichment import LiveTelemetryEnricher
from app.services.telemetry_clients import TelemetryClients
from app.telemetry.metrics import AI_RCA_DURATION_SECONDS, AI_RCA_INFERENCE_SECONDS, AI_RCA_REQUESTS_TOTAL, AI_RCA_TOKEN_USAGE_TOTAL

logger = logging.getLogger("ai-rca.workflow")


class RCAWorkflow:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.telemetry = TelemetryClients(settings)
        self.enricher = LiveTelemetryEnricher(self.telemetry)
        self.artifacts = RCAArtifactStore(settings.artifact_dir)

    async def analyze(self, context: IncidentContext, workflow: str = "rca") -> RCAResponse:
        if not context.grafana_links:
            context.grafana_links = build_grafana_links(context, self.settings)
        provider = build_provider(self.settings)
        prompt = self._build_prompt(context, workflow)
        started = time.perf_counter()
        outcome = "success"
        try:
            result = await provider.generate_rca(context, prompt)
            response = result.response
        except Exception:
            outcome = "error"
            raise
        finally:
            elapsed = time.perf_counter() - started
            provider_name = getattr(provider, "name", self.settings.ai_provider)
            AI_RCA_REQUESTS_TOTAL.labels(workflow=workflow, provider=provider_name, outcome=outcome).inc()
            AI_RCA_DURATION_SECONDS.labels(workflow=workflow, provider=provider_name, outcome=outcome).observe(elapsed)
        AI_RCA_INFERENCE_SECONDS.labels(provider=response.provider, model=response.model, outcome="success").observe(
            time.perf_counter() - started
        )
        AI_RCA_TOKEN_USAGE_TOTAL.labels(provider=response.provider, model=response.model, type="prompt").inc(result.prompt_tokens)
        AI_RCA_TOKEN_USAGE_TOTAL.labels(provider=response.provider, model=response.model, type="completion").inc(result.completion_tokens)
        logger.info(
            "ai rca workflow completed",
            extra={
                "provider": response.provider,
                "model": response.model,
                "workflow": workflow,
                "outcome": "success",
                "incident_id": context.incident_id,
                "alert_name": context.alert.name if context.alert else None,
            },
        )
        return response

    async def analyze_alertmanager_webhook(self, payload: AlertmanagerWebhook) -> WebhookRCAResult:
        analyses: list[RCAResponse] = []
        artifacts = []
        for alert in payload.alerts:
            context = incident_from_alert(alert)
            enriched = await self.enricher.enrich(context)
            response = await self.analyze(enriched, workflow="alertmanager-webhook")
            analyses.append(response)
            artifacts.append(self.artifacts.persist(enriched, response))
        return WebhookRCAResult(received_alerts=len(payload.alerts), generated=artifacts, analyses=analyses)

    def _build_prompt(self, context: IncidentContext, workflow: str) -> str:
        base = load_prompt("rca-generation")
        payload = context.model_dump_json(indent=2)
        max_chars = self.settings.ai_max_input_chars
        return f"{base}\n\nWorkflow: {workflow}\nTelemetry JSON:\n{payload[:max_chars]}"
