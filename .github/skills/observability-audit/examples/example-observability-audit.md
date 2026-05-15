# Example Observability Audit Finding

| Severity | Area | Finding | Evidence | Recommended Action |
| --- | --- | --- | --- | --- |
| Medium | Metrics | API target missing from Prometheus | `/api/v1/targets` shows API down | Check Alloy scrape config and API `/metrics` readiness |
