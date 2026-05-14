# SLO and Error Budget Model

OpsSight implements a local SRE-style SLO model for the API service.

## SLIs

- Availability: `1 - 5xx_ratio`
- Latency compliance: requests under the 1 second histogram bucket divided by total requests
- Error rate: 5xx responses divided by total requests

## SLOs

- Availability: 99.9%
- Latency: p95 below 1 second
- Error rate: budgeted through the 99.9% availability objective

## Burn Rate

Burn rate compares current bad-event ratio against the allowed error budget. A burn rate of `1` means the service is consuming budget exactly at the allowed pace. A burn rate above `14` means the budget is being consumed fast enough to justify urgent response.

Prometheus rules:

```promql
opsight:slo_availability_burn_rate:5m
opsight:slo_availability_burn_rate:1h
opsight:slo_availability_burn_rate:6h
opsight:slo_error_budget_remaining:30d
```

Alerts:

- `OpsSightSLOFastBurn`
- `OpsSightSLOSlowBurn`
