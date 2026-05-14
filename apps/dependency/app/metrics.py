from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

PAYMENT_REQUESTS_TOTAL = Counter(
    "opsight_payment_requests_total",
    "Payment dependency requests.",
    ["operation", "status_code", "outcome"],
)
PAYMENT_DURATION_SECONDS = Histogram(
    "opsight_payment_duration_seconds",
    "Payment dependency request duration.",
    ["operation", "outcome"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
PAYMENT_ACTIVE_REQUESTS = Gauge("opsight_payment_active_requests", "Active payment dependency requests.")


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
