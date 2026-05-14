from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

AI_RCA_REQUESTS_TOTAL = Counter(
    "opsight_ai_rca_requests_total",
    "AI RCA workflow requests.",
    ["workflow", "provider", "outcome"],
)
AI_RCA_DURATION_SECONDS = Histogram(
    "opsight_ai_rca_duration_seconds",
    "AI RCA workflow duration.",
    ["workflow", "provider", "outcome"],
    buckets=(0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)
AI_RCA_PROVIDER_FAILURES_TOTAL = Counter(
    "opsight_ai_rca_provider_failures_total",
    "LLM provider failures that required fallback or degraded output.",
    ["provider", "reason"],
)
AI_RCA_INFERENCE_SECONDS = Histogram(
    "opsight_ai_rca_inference_seconds",
    "LLM or rule-based inference duration.",
    ["provider", "model", "outcome"],
    buckets=(0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)
AI_RCA_TOKEN_USAGE_TOTAL = Counter(
    "opsight_ai_rca_token_usage_total",
    "Provider-reported or estimated token usage.",
    ["provider", "model", "type"],
)
AI_RCA_ACTIVE_REQUESTS = Gauge("opsight_ai_rca_active_requests", "Active AI RCA workflow requests.")


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
