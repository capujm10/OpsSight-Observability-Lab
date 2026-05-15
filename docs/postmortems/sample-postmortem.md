# Sample Postmortem: Dependency Outage During Local Smoke Validation

## Summary

The local smoke test failed because the Orders API could not complete the `/api/v1/orders` request path while the payment-gateway dependency was unavailable. Core observability backends were healthy, which narrowed the incident to the application dependency path rather than a full stack outage.

## Impact

- API readiness remained available.
- The sample orders endpoint failed or returned degraded behavior.
- Metrics and logs captured the dependency failure path.
- The demo environment was not ready for incident walkthroughs until the dependency recovered.

## Timeline

| Time | Event |
| --- | --- |
| T+0m | Smoke test started. |
| T+1m | API and observability backend readiness checks passed. |
| T+2m | Orders endpoint check failed. |
| T+3m | Dependency logs showed unavailable payment-gateway behavior. |
| T+5m | Dependency service restarted and readiness recovered. |
| T+6m | Smoke test passed. |

## Root Cause

The payment-gateway dependency was not healthy when the API request path was validated. The API surfaced the failure through structured logs, metrics, and HTTP status behavior.

## Detection

- `bash scripts/smoke-test.sh`
- API logs with dependency failure context
- Prometheus request/error metrics
- Grafana API golden signals dashboard

## What Went Well

- Smoke testing caught the regression before a demo or publication workflow.
- Service-level logs included correlation context.
- Observability backends stayed available for investigation.

## Follow-Up Actions

- Keep dependency readiness as a required smoke test condition.
- Preserve API and dependency service logs in failed CI runs.
- Add screenshots for the dependency failure investigation path.
- Review Compose dependency health settings after any service startup changes.
