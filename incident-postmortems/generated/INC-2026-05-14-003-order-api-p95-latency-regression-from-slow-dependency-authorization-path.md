# Latency Incident Postmortem: Order API p95 latency regression from slow dependency authorization path

This template focuses on p95/p99 latency, slow endpoints, dependency spans, saturation, and user-perceived performance.

| Field | Value |
| --- | --- |
| Incident ID | `INC-2026-05-14-003` |
| Severity | `SEV-3` |
| Status | `Resolved` |
| Owner | `Backend Platform` |
| Started | `2026-05-14 03:58 UTC` |
| Resolved | `2026-05-14 04:04 UTC` |
| Duration | `6 minutes` |

## Impact Summary

Synthetic latency traffic increased p95 latency for order workflows that call payment-gateway authorization. The API remained available, but user-perceived response time degraded during the scenario.

## Affected Systems

- opsight-api /api/v1/simulate/latency
- payment-gateway authorize operation
- OpsSight API Golden Signals latency panels

## Customer Impact

Requests completed more slowly but did not fail. The issue was limited to dependency-backed paths and did not affect liveness or readiness.

## Detection

- Method: High p95 latency alert and Golden Signals latency panel.
- Alert triggered: `OpsSightHighP95Latency`
- SLO burn: Latency SLI degraded; availability error budget was not directly consumed because requests completed successfully.

## Timeline

- 2026-05-14 03:58 UTC - p95 latency crossed the operational threshold.
- 2026-05-14 03:59 UTC - On-call compared API latency p95 with dependency latency p95.
- 2026-05-14 04:00 UTC - Tempo traces showed long payment_gateway.http_call spans.
- 2026-05-14 04:02 UTC - Latency simulation was stopped.
- 2026-05-14 04:04 UTC - p95 latency returned below target and smoke test passed.

## Latency Root Cause

The payment-gateway authorization path was intentionally slowed, increasing the duration of API spans waiting on the dependency client call.

## Contributing Factors

- Dependency latency directly influenced the API critical path.
- No cache or degraded response mode existed for dependency-backed order workflows.
- The latency scenario generated enough slow spans to affect p95.

## Mitigation Steps

- Stopped latency simulation traffic.
- Confirmed payment-gateway health and metrics endpoint remained healthy.
- Compared p95 latency before and after mitigation.
- Verified traces no longer contained slow dependency spans.

## Resolution

Latency returned to baseline after simulated dependency slowness stopped.

## Recovery Validation

- API p95 latency returned below 1 second.
- k6 smoke profile passed latency threshold.
- Tempo traces showed normal dependency span duration.
- No 5xx increase accompanied the latency event.

## Preventive Actions

- Add timeout budget documentation for dependency calls.
- Add dashboard panel for slowest dependency operations.
- Evaluate async fallback behavior for non-critical dependency metadata.

## Follow-Up Tasks

| Task | Owner | Priority | Status |
| --- | --- | --- | --- |
| Define per-dependency timeout budgets. | Backend Platform | P2 | Open |
| Add dependency p95/p99 split by operation to SRE Overview. | Observability | P3 | Open |

## Lessons Learned

- Trace span duration is the fastest way to distinguish API compute latency from dependency wait time.
- Latency incidents can be customer-impacting even without availability burn.

## AI-Assisted RCA Enrichment

No AI RCA enrichment was attached for this incident. Generate one through `apps/ai-rca` before final review if telemetry context is available.

## Telemetry References

### Grafana Dashboards
- OpsSight API Golden Signals: /d/opsight-api-golden-signals/opsight-api-golden-signals
- OpsSight Incident Investigation: /d/opsight-incident-investigation/opsight-incident-investigation

### Prometheus Queries
- `histogram_quantile(0.95, sum(rate(opsight_http_request_duration_seconds_bucket[5m])) by (le, route))`
- `histogram_quantile(0.95, sum(rate(opsight_dependency_latency_seconds_bucket[5m])) by (le, dependency, operation))`

### Loki Queries
- `{service="opsight-api"} | json | scenario="high_latency"`
- `{service="opsight-api"} | json | path="/api/v1/simulate/latency"`

### Tempo Trace References
- trace_id=1294f055d7c8b0600ff6e7d797d5d0de

### Correlation IDs
- latency-scenario-1

## Grafana Operational Annotations

```json
[
  {
    "tags": [
      "opsight",
      "SEV-3",
      "incident_start",
      "INC-2026-05-14-003"
    ],
    "text": "p95 latency crossed the operational threshold.",
    "time": 1778731080000
  },
  {
    "tags": [
      "opsight",
      "SEV-3",
      "mitigation_deployed",
      "INC-2026-05-14-003"
    ],
    "text": "Latency simulation was stopped.",
    "time": 1778731350000
  },
  {
    "tags": [
      "opsight",
      "SEV-3",
      "recovery_confirmed",
      "INC-2026-05-14-003"
    ],
    "text": "p95 latency returned below target and smoke test passed.",
    "time": 1778731470000
  }
]
```
