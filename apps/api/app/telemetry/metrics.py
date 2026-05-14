from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

HTTP_REQUESTS_TOTAL = Counter(
    "opsight_http_requests_total",
    "Total HTTP requests processed by the API.",
    ["method", "route", "status_code"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "opsight_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
HTTP_ACTIVE_REQUESTS = Gauge(
    "opsight_http_active_requests",
    "In-flight HTTP requests.",
    ["method", "route"],
)
DEPENDENCY_LATENCY_SECONDS = Histogram(
    "opsight_dependency_latency_seconds",
    "Simulated downstream dependency latency in seconds.",
    ["dependency", "operation", "outcome"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
DEPENDENCY_FAILURES_TOTAL = Counter(
    "opsight_dependency_failures_total",
    "Simulated downstream dependency failures.",
    ["dependency", "operation"],
)
ORDERS_CREATED_TOTAL = Counter("opsight_orders_created_total", "Orders created through the API.")


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
