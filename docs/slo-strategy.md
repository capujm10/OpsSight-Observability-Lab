# SLO Strategy

OpsSight models a local-first SLO workflow for the API service. The goal is operational realism: use service-level indicators, burn-rate style alerts, and dashboards to explain when an incident should interrupt normal work.

## Service-Level Indicators

Primary API indicators:

- Availability: successful API requests divided by total API requests.
- Latency compliance: requests served under the one-second bucket.
- Error rate: 5xx API responses divided by total API requests.
- Saturation: active API, payment-gateway, and AI RCA request gauges.

Supporting dependency indicators:

- Payment-gateway p95 latency.
- Payment-gateway failure rate.
- API dependency latency and failure counters.

## Recording Rules

Prometheus recording rules in `observability/prometheus/rules/recording-rules.yml` define reusable series:

- `opsight:sli_availability:5m`
- `opsight:sli_latency_compliance:5m`
- `opsight:sli_error_rate:5m`
- `opsight:api_latency_p95:5m`
- `opsight:dependency_latency_p95:5m`
- `opsight:slo_availability_burn_rate:5m`
- `opsight:slo_availability_burn_rate:1h`
- `opsight:slo_availability_burn_rate:6h`
- `opsight:slo_error_budget_remaining:30d`

## Dashboards

The provisioned dashboard `OpsSight SLO Operational Maturity` focuses on:

- API latency
- error rate
- request throughput
- dependency latency
- saturation indicators
- burn-rate alert visibility
- recent warning and error logs

Use it with `OpsSight API Golden Signals` and `OpsSight Incident Investigation` during incident review.

## Alerting Model

Burn-rate alerts are intentionally simple and local-demo friendly:

- `OpsSightSLOFastBurn` catches rapid availability budget burn.
- `OpsSightSLOSlowBurn` catches sustained budget burn.
- `OpsSightExcessiveErrorRate` catches high immediate error ratios.
- `OpsSightDependencyDegradation` ties upstream degradation to API impact.

These alerts are not a substitute for production SLO calibration. They are designed to demonstrate the workflow and provide clear local evidence.

## Review Workflow

1. Generate baseline traffic with `make load`.
2. Run `make incident-sim` or a focused scenario.
3. Open the SLO dashboard and inspect availability, error budget, burn rate, and dependency latency.
4. Pivot to Loki by `correlation_id` or `trace_id`.
5. Confirm Tempo traces show the expected API-to-payment-gateway path.
6. Run `bash scripts/smoke-test.sh` and `bash scripts/synthetic-monitor.sh` after recovery.
