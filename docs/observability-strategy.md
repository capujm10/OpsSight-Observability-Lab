# Observability Strategy

The service follows the three-signal model used by modern SRE teams:

- Metrics answer whether the service is healthy and how badly users are affected.
- Logs explain what happened at a specific point in time with correlation IDs and trace IDs.
- Traces show where time was spent across the request path and simulated dependency calls.

Primary operational views:

- Golden signals: rate, errors, duration, saturation.
- Dependency health: latency and failure count for the simulated payment gateway.
- Incident investigation: logs, traces, route-level latency, and failure drilldowns.
- SRE overview: availability SLI, burn rate, error budget, dependency posture, and active alerts.

SLO model:

- Availability objective: 99.9%.
- Latency objective: p95 below 1 second.
- Error-rate objective: keep 5xx ratio below the 0.1% availability budget.
- Burn-rate windows: 5m, 1h, and 6h.

Useful PromQL:

```promql
sum(rate(opsight_http_requests_total[5m])) by (route, method)
sum(rate(opsight_http_requests_total{status_code=~"5.."}[5m]))
histogram_quantile(0.95, sum(rate(opsight_http_request_duration_seconds_bucket[5m])) by (le, route))
histogram_quantile(0.95, sum(rate(opsight_dependency_latency_seconds_bucket[5m])) by (le, dependency, operation))
opsight:slo_availability_burn_rate:5m
opsight:slo_error_budget_remaining:30d
sum(rate(opsight_payment_requests_total{status_code=~"5.."}[5m]))
```

Useful LogQL:

```logql
{service="opsight-api"} | json
{service="opsight-api",severity="ERROR"} | json
{service="opsight-api"} | json | correlation_id="your-correlation-id"
{service="opsight-api"} | json | trace_id="your-trace-id"
{service=~"opsight-api|payment-gateway"} | json | severity =~ "ERROR|WARNING"
```
