import time

import httpx
from opentelemetry import trace
from opentelemetry.propagate import inject

from app.config.settings import Settings
from app.log_context.context import get_correlation_id
from app.middleware.errors import DependencyFailure
from app.telemetry.metrics import DEPENDENCY_FAILURES_TOTAL, DEPENDENCY_LATENCY_SECONDS

tracer = trace.get_tracer(__name__)


async def observed_dependency_call(
    settings: Settings,
    operation: str = "authorize",
    force_failure: bool = False,
    latency_multiplier: float = 1.0,
) -> dict[str, str]:
    dependency = "payment-gateway"
    started = time.perf_counter()
    outcome = "success"
    with tracer.start_as_current_span("payment_gateway.http_call") as span:
        span.set_attribute("dependency.name", dependency)
        span.set_attribute("dependency.operation", operation)
        span.set_attribute("http.url", settings.dependency_url)
        headers: dict[str, str] = {}
        inject(headers)
        headers["x-correlation-id"] = get_correlation_id()
        payload = {
            "operation": operation,
            "force_failure": force_failure,
            "latency_multiplier": latency_multiplier,
        }
        try:
            async with httpx.AsyncClient(timeout=settings.dependency_timeout_seconds) as client:
                response = await client.post(f"{settings.dependency_url}/api/v1/payments/authorize", json=payload, headers=headers)
            span.set_attribute("http.status_code", response.status_code)
            if response.status_code >= 500:
                outcome = "failure"
                DEPENDENCY_FAILURES_TOTAL.labels(dependency=dependency, operation=operation).inc()
                span.set_attribute("error", True)
                raise DependencyFailure("payment gateway degraded or unavailable")
            response.raise_for_status()
            return response.json()
        except (httpx.TimeoutException, httpx.HTTPError) as exc:
            outcome = "failure"
            DEPENDENCY_FAILURES_TOTAL.labels(dependency=dependency, operation=operation).inc()
            span.set_attribute("error", True)
            span.set_attribute("dependency.outcome", outcome)
            raise DependencyFailure("payment gateway degraded or unavailable") from exc
        finally:
            duration = time.perf_counter() - started
            DEPENDENCY_LATENCY_SECONDS.labels(dependency=dependency, operation=operation, outcome=outcome).observe(duration)
