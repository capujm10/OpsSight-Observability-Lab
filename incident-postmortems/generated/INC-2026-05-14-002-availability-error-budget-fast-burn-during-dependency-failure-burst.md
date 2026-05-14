# SLO Burn Incident Postmortem: Availability error budget fast burn during dependency failure burst

This template emphasizes error budget impact, burn-rate windows, and product/engineering tradeoffs after SLO breach risk.

| Field | Value |
| --- | --- |
| Incident ID | `INC-2026-05-14-002` |
| Severity | `SEV-1` |
| Status | `Resolved` |
| Owner | `SRE` |
| Started | `2026-05-14 04:11 UTC` |
| Resolved | `2026-05-14 04:18 UTC` |
| Duration | `6 minutes` |

## SLO Impact Summary

A concentrated burst of dependency-induced 503 responses drove the availability burn rate well above the fast-burn threshold for the 99.9% API availability SLO.

## Affected Systems

- opsight-api availability SLO
- payment-gateway dependency
- Prometheus burn-rate alerts

## Customer Impact

A subset of order requests failed while dependency-backed operations were unhealthy. Existing successful orders were unaffected, but users relying on the order API experienced failed requests until the failure burst stopped.

## Detection

- Method: Multi-window SLO burn-rate alerting in Prometheus.
- Alert triggered: `OpsSightSLOFastBurn`
- Error budget burn: 5m burn rate reached approximately 120x; 1h burn rate exceeded the fast-burn threshold after repeated 503s.

## Timeline

- 2026-05-14 04:11 UTC - OpsSightSLOFastBurn entered pending after availability burn exceeded threshold.
- 2026-05-14 04:13 UTC - Fast-burn alert entered firing state.
- 2026-05-14 04:14 UTC - SRE Overview confirmed error budget remaining was being consumed rapidly.
- 2026-05-14 04:14 UTC - Top failing endpoint analysis identified dependency-failure route as dominant bad-event source.
- 2026-05-14 04:15 UTC - Failure scenario traffic stopped and baseline smoke traffic resumed.
- 2026-05-14 04:18 UTC - No new 503 burst observed; burn-rate trend began decreasing.

## Root Cause

The 99.9% availability error budget was rapidly consumed by a controlled dependency-failure burst that generated sustained 503 responses from API routes dependent on payment-gateway.

## Contributing Factors

- Repeated forced dependency failures produced a dense bad-event window.
- The fast-burn alert used a realistic threshold requiring enough sustained bad events to avoid noise.
- The API correctly preserved dependency failure semantics instead of hiding failures.

## Mitigation Steps

- Stopped the synthetic dependency failure generator.
- Confirmed payment-gateway health was green after traffic stopped.
- Ran smoke tests to verify the API and dependency were reachable.
- Checked SLO burn-rate panels for recovery trend.

## Resolution

The incident was resolved after failure generation stopped and successful requests dominated the rolling burn windows.

## Recovery Validation

- OpsSightSLOFastBurn was observed firing from real telemetry.
- Smoke test passed after mitigation.
- Cross-service traces showed successful payment-gateway spans.
- Prometheus up metrics remained healthy for both services.

## Preventive Actions

- Document a policy for pausing feature work when remaining budget drops below threshold.
- Add projected budget exhaustion panel to the SRE Overview dashboard.
- Add runbook links directly in alert annotations.

## Follow-Up Tasks

| Task | Owner | Priority | Status |
| --- | --- | --- | --- |
| Add explicit SLO freeze policy to docs/slo-error-budget.md. | SRE | P1 | Open |
| Add projected exhaustion calculation to dashboard roadmap. | Observability | P2 | Open |

## Lessons Learned

- Burn-rate alerts provide stronger operational signal than raw 5xx alerts during concentrated failure bursts.
- SLO panels must be close to incident dashboards so responders can evaluate user impact quickly.

## AI-Assisted RCA Enrichment

No AI RCA enrichment was attached for this incident. Generate one through `apps/ai-rca` before final review if telemetry context is available.

## Telemetry References

### Grafana Dashboards
- OpsSight SRE Overview: /d/opsight-sre-overview/opsight-sre-overview
- OpsSight API Golden Signals: /d/opsight-api-golden-signals/opsight-api-golden-signals

### Prometheus Queries
- `opsight:slo_availability_burn_rate:5m`
- `opsight:slo_availability_burn_rate:1h`
- `opsight:slo_error_budget_remaining:30d`
- `sum(rate(opsight_http_requests_total{status_code=~"5.."}[5m]))`

### Loki Queries
- `{service="opsight-api",severity="ERROR"} | json`
- `{service="opsight-api"} | json | status_code="503"`

### Tempo Trace References
- trace_id=27a51aae7664ac0c0708c9af0ec80334

### Correlation IDs
- trace-chain-check

## Grafana Operational Annotations

```json
[
  {
    "tags": [
      "opsight",
      "SEV-1",
      "incident_start",
      "INC-2026-05-14-002"
    ],
    "text": "OpsSightSLOFastBurn entered pending after availability burn exceeded threshold.",
    "time": 1778731916000
  },
  {
    "tags": [
      "opsight",
      "SEV-1",
      "mitigation_deployed",
      "INC-2026-05-14-002"
    ],
    "text": "Failure scenario traffic stopped and baseline smoke traffic resumed.",
    "time": 1778732115000
  },
  {
    "tags": [
      "opsight",
      "SEV-1",
      "recovery_confirmed",
      "INC-2026-05-14-002"
    ],
    "text": "No new 503 burst observed; burn-rate trend began decreasing.",
    "time": 1778732300000
  }
]
```
