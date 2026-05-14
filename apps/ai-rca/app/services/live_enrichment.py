from __future__ import annotations

from typing import Any

from app.models.rca import IncidentContext, TelemetrySignal
from app.services.telemetry_clients import TelemetryClients


class LiveTelemetryEnricher:
    def __init__(self, clients: TelemetryClients) -> None:
        self.clients = clients

    async def enrich(self, context: IncidentContext) -> IncidentContext:
        service = context.alert.service if context.alert else _first(context.affected_services, "opsight-api")
        await self._prometheus(context, service)
        await self._loki(context, service)
        await self._tempo(context)
        return context

    async def _prometheus(self, context: IncidentContext, service: str) -> None:
        queries = {
            "availability_burn_rate_5m": "opsight:slo_availability_burn_rate:5m",
            "availability_burn_rate_1h": "opsight:slo_availability_burn_rate:1h",
            "api_error_rate_5m": (
                '(sum(rate(opsight_http_requests_total{status_code=~"5.."}[5m])) or vector(0)) / '
                "clamp_min(sum(rate(opsight_http_requests_total[5m])), 1)"
            ),
            "api_p95_latency_seconds": ("histogram_quantile(0.95, sum(rate(opsight_http_request_duration_seconds_bucket[5m])) by (le))"),
            "dependency_p95_latency_seconds": (
                "histogram_quantile(0.95, sum(rate(opsight_payment_duration_seconds_bucket[5m])) by (le, operation))"
            ),
            "service_up": f'avg(up{{job="{service}"}})',
        }
        for name, query in queries.items():
            result = await self.clients.prometheus_query(query)
            value = _prometheus_scalar(result)
            context.metrics.append(TelemetrySignal(name=name, value=value, description=query))
            if value is None:
                continue
            if name == "availability_burn_rate_5m":
                context.burn_rate = value
            elif name == "api_error_rate_5m":
                context.error_rate = value
            elif name == "api_p95_latency_seconds":
                context.p95_latency_seconds = value
        if context.burn_rate and context.burn_rate > 1 and "availability-99.9" not in context.impacted_slos:
            context.impacted_slos.append("availability-99.9")
        if context.p95_latency_seconds and context.p95_latency_seconds > 1 and "api-p95-latency" not in context.impacted_slos:
            context.impacted_slos.append("api-p95-latency")

    async def _loki(self, context: IncidentContext, service: str) -> None:
        queries = [
            f'{{service="{service}"}} | json | severity =~ "ERROR|WARNING"',
        ]
        if context.alert and context.alert.severity:
            queries.append(f'{{service="{service}"}} | json | severity="{context.alert.severity.upper()}"')
        for trace_id in context.traces.trace_ids:
            queries.append(f'{{service=~"{service}|payment-gateway|opsight-ai-rca"}} | json | trace_id="{trace_id}"')
        for correlation_id in context.logs.correlation_ids:
            queries.append(f'{{service=~"{service}|payment-gateway|opsight-ai-rca"}} | json | correlation_id="{correlation_id}"')

        seen = set(context.logs.loki_queries)
        for query in queries:
            if query not in seen:
                context.logs.loki_queries.append(query)
                seen.add(query)
            result = await self.clients.loki_query_range(query)
            for pattern in _loki_patterns(result):
                if pattern not in context.logs.patterns:
                    context.logs.patterns.append(pattern)

    async def _tempo(self, context: IncidentContext) -> None:
        for trace_id in context.traces.trace_ids:
            result = await self.clients.tempo_trace(trace_id)
            summary = _tempo_summary(result)
            for service in summary["services"]:
                if service not in context.traces.services:
                    context.traces.services.append(service)
            for span in summary["slow_spans"]:
                if span not in context.traces.slow_spans:
                    context.traces.slow_spans.append(span)
            for span in summary["failed_spans"]:
                if span not in context.traces.failed_spans:
                    context.traces.failed_spans.append(span)


def _prometheus_scalar(payload: dict[str, Any]) -> float | None:
    try:
        results = payload["data"]["result"]
        if not results:
            return None
        return float(results[0]["value"][1])
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def _loki_patterns(payload: dict[str, Any]) -> list[str]:
    patterns: list[str] = []
    try:
        streams = payload["data"]["result"]
    except (KeyError, TypeError):
        return patterns
    for stream in streams[:5]:
        labels = stream.get("stream", {})
        values = stream.get("values", [])
        severity = labels.get("severity")
        if severity:
            patterns.append(f"severity={severity}")
        for value in values[:3]:
            line = value[1]
            if "503" in line:
                patterns.append("status_code=503")
            if "dependency" in line.lower():
                patterns.append("dependency_failure_pattern")
            if "timeout" in line.lower():
                patterns.append("timeout_pattern")
    return list(dict.fromkeys(patterns))


def _tempo_summary(payload: dict[str, Any]) -> dict[str, list[str]]:
    services: list[str] = []
    slow_spans: list[str] = []
    failed_spans: list[str] = []
    batches = payload.get("batches") or payload.get("data", {}).get("batches", [])
    for batch in batches:
        resource_attrs = _attrs(batch.get("resource", {}).get("attributes", []))
        service = resource_attrs.get("service.name")
        if service and service not in services:
            services.append(service)
        for scope_span in batch.get("scopeSpans", []) + batch.get("instrumentationLibrarySpans", []):
            for span in scope_span.get("spans", []):
                name = span.get("name", "span")
                duration_ms = _span_duration_ms(span)
                status = span.get("status", {}).get("code")
                if duration_ms and duration_ms > 500:
                    slow_spans.append(f"{service or 'unknown'} {name} {duration_ms:.0f}ms")
                if status in {"STATUS_CODE_ERROR", 2}:
                    failed_spans.append(f"{service or 'unknown'} {name}")
    return {"services": services, "slow_spans": slow_spans, "failed_spans": failed_spans}


def _attrs(values: list[dict[str, Any]]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in values:
        value = item.get("value", {})
        parsed[item.get("key", "")] = str(value.get("stringValue") or value.get("intValue") or value.get("doubleValue") or "")
    return parsed


def _span_duration_ms(span: dict[str, Any]) -> float | None:
    try:
        start = int(span["startTimeUnixNano"])
        end = int(span["endTimeUnixNano"])
        return (end - start) / 1_000_000
    except (KeyError, TypeError, ValueError):
        return None


def _first(values: list[str], default: str) -> str:
    return values[0] if values else default
