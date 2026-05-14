# Dependency Degradation Postmortem: Payment gateway dependency degradation caused elevated order API 503s

This template focuses on upstream service health, dependency latency, fallback behavior, and trace-based causality.

| Field | Value |
| --- | --- |
| Incident ID | `INC-2026-05-14-001` |
| Severity | `SEV-2` |
| Status | `Resolved` |
| Owner | `Platform SRE` |
| Started | `2026-05-14 04:08 UTC` |
| Resolved | `2026-05-14 04:15 UTC` |
| Duration | `7 minutes` |

## Impact Summary

The Orders API returned intermittent 503 responses when the payment-gateway dependency returned forced failures. Availability stayed above complete outage level, but the API entered a customer-visible partial failure mode for order listing and creation workflows that require dependency state.

## Affected Systems

- opsight-api /api/v1/orders
- payment-gateway /api/v1/payments/authorize
- Grafana SRE Overview and Incident Investigation dashboards

## Customer Impact

Users attempting order workflows saw intermittent server errors. Readiness and liveness remained healthy, so the incident presented as a partial service degradation rather than full API downtime.

## Detection

- Method: Prometheus dependency and 5xx alerts surfaced the degradation after repeated dependency-failure simulations.
- Alert triggered: `OpsSightPaymentGatewayErrors, OpsSightDependencyDegradation, OpsSightElevated5xxResponses`
- SLO burn: 5m burn rate exceeded 100x during the forced failure burst; fast-burn alert entered firing state after the configured for-window.

## Timeline

- 2026-05-14 04:08 UTC - Payment gateway 5xx responses detected by Prometheus.
- 2026-05-14 04:08 UTC - OpsSightDependencyDegradation alert entered firing state.
- 2026-05-14 04:09 UTC - On-call reviewed Incident Investigation dashboard and confirmed 503s were isolated to dependency-backed paths.
- 2026-05-14 04:10 UTC - Tempo traces showed API client spans receiving 503 responses from payment-gateway server spans.
- 2026-05-14 04:11 UTC - OpsSightSLOFastBurn entered pending after sustained error budget burn.
- 2026-05-14 04:13 UTC - Failure generation stopped and dependency service returned to baseline behavior.
- 2026-05-14 04:15 UTC - API smoke test and SLO burn checks confirmed recovery trend.

## Dependency Root Cause

The payment-gateway dependency returned 503 responses during an explicit degradation scenario. The Orders API propagated those dependency failures as service-unavailable responses for routes requiring payment state.

## Contributing Factors

- Dependency-backed order paths had no fallback response mode.
- The API correctly surfaced dependency failure as 503, which protected data correctness but exposed user-facing errors.
- High failure burst consumed error budget quickly before mitigation.

## Mitigation Steps

- Stopped dependency-failure traffic generation.
- Confirmed payment-gateway health endpoint and metrics endpoint were healthy.
- Verified API route recovery through smoke tests and Prometheus request status distribution.
- Used Tempo to verify successful cross-service spans after mitigation.

## Resolution

The dependency was restored to normal behavior and dependency-backed API requests returned 200 responses. No data repair was required because failed requests did not mutate order state.

## Recovery Validation

- bash scripts/smoke-test.sh passed.
- up{job=~"opsight-api|payment-gateway"} returned 1 for both services.
- Loki showed no new dependency failure logs after mitigation.
- Tempo traces showed successful API-to-payment-gateway spans.
- SLO burn rate began trending down after failure traffic stopped.

## Preventive Actions

- Add a dependency-specific runbook for fallback and retry decisions.
- Add a circuit-breaker design note for dependency-backed order workflows.
- Add dashboard drilldown from top failing endpoints to payment-gateway error panels.
- Define acceptable degraded-mode behavior for read-only order listing.

## Follow-Up Tasks

| Task | Owner | Priority | Status |
| --- | --- | --- | --- |
| Document fallback behavior for dependency-backed read paths. | Platform SRE | P1 | Open |
| Add dependency circuit-breaker implementation candidate to roadmap. | Backend Engineering | P2 | Open |
| Add dashboard panel for payment-gateway status-code split. | Observability | P2 | Open |

## Lessons Learned

- Cross-service traces made it clear the API was healthy but dependency-backed operations were failing.
- Error budget burn helped distinguish a contained dependency fault from a low-severity isolated error.
- Dependency-specific alerts reduced time spent inspecting unrelated API internals.

## AI-Assisted RCA Enrichment

> AI-generated operational analysis. Validate against Prometheus, Loki, Tempo, deployment history, and incident commander notes before treating as final RCA.

### AI Incident Summary

opsight-api experienced elevated 503s and accelerated availability SLO burn from payment-gateway dependency degradation, with failures visible across logs and Tempo cross-service spans.

### AI Telemetry Interpretation

Prometheus 5xx and burn-rate metrics show user-visible availability impact, Loki patterns isolate dependency-backed API failures, and Tempo trace IDs identify propagation from opsight-api client spans into payment-gateway server spans.

### AI RCA Hypotheses

1. **payment-gateway latency or failure degradation**
   - Confidence: high
   - Supporting telemetry:
- OpsSightPaymentGatewayErrors firing
- payment-gateway outcome=failure logs
- Tempo traces 27a51aae7664ac0c0708c9af0ec80334 and 1294f055d7c8b0600ff6e7d797d5d0de
   - Validation steps:
- Inspect payment-gateway spans in Tempo for 503 status and duration.
- Compare opsight_payment_requests_total 5xx rate against opsight_http_requests_total 5xx rate.
- Filter Loki by correlation_id=trace-chain-check across both services.

2. **availability SLO fast burn from concentrated dependency-backed 503 responses**
   - Confidence: high
   - Supporting telemetry:
- opsight:slo_availability_burn_rate:5m exceeded fast-burn threshold
- OpsSightElevated5xxResponses alert fired
   - Validation steps:
- Review SRE Overview burn-rate panel over the incident window.
- Confirm recovery trend after mitigation using 5m and 1h burn windows.

### AI Remediation Suggestions

- Keep incident ownership active until dependency-backed order routes show sustained 2xx recovery.
- Add circuit-breaker and degraded-mode design for read-only order workflows.
- Add direct dashboard drilldown from top failing endpoints to payment-gateway logs and traces.

### AI Risk Notes

- The AI summary is an investigation aid and must be validated against source telemetry before final RCA.
- Error budget recovery lags mitigation, so incident closure should wait for rolling-window confirmation.

## Telemetry References

### Grafana Dashboards
- OpsSight SRE Overview: /d/opsight-sre-overview/opsight-sre-overview
- OpsSight Incident Investigation: /d/opsight-incident-investigation/opsight-incident-investigation

### Prometheus Queries
- `sum(rate(opsight_payment_requests_total{status_code=~"5.."}[5m]))`
- `sum(rate(opsight_http_requests_total{status_code=~"5.."}[5m]))`
- `opsight:slo_availability_burn_rate:5m`
- `up{job=~"opsight-api|payment-gateway"}`

### Loki Queries
- `{service="opsight-api",severity="ERROR"} | json | path="/api/v1/simulate/dependency-failure"`
- `{service="payment-gateway"} | json | outcome="failure"`
- `{service=~"opsight-api|payment-gateway"} | json | correlation_id="trace-chain-check"`

### Tempo Trace References
- trace_id=27a51aae7664ac0c0708c9af0ec80334
- trace_id=1294f055d7c8b0600ff6e7d797d5d0de

### Correlation IDs
- trace-chain-check
- sre-validation

## Grafana Operational Annotations

```json
[
  {
    "tags": [
      "opsight",
      "SEV-2",
      "incident_start",
      "INC-2026-05-14-001"
    ],
    "text": "Payment gateway 5xx responses detected by Prometheus.",
    "time": 1778731691000
  },
  {
    "tags": [
      "opsight",
      "SEV-2",
      "mitigation_deployed",
      "INC-2026-05-14-001"
    ],
    "text": "Failure generation stopped and dependency service returned to baseline behavior.",
    "time": 1778732000000
  },
  {
    "tags": [
      "opsight",
      "SEV-2",
      "recovery_confirmed",
      "INC-2026-05-14-001"
    ],
    "text": "API smoke test and SLO burn checks confirmed recovery trend.",
    "time": 1778732130000
  }
]
```
