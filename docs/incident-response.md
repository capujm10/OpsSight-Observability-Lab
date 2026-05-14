# Incident Response

1. Confirm impact in the API Golden Signals dashboard.
2. Identify the affected route, status code, and latency percentile.
3. Open the Incident Investigation dashboard.
4. Query error logs and copy the `trace_id` or `correlation_id`.
5. Open Tempo from the Loki derived field or paste the trace ID into Explore.
6. Inspect dependency spans and application exceptions.
7. Apply mitigation: stop load, restart the service, roll back config, or isolate dependency behavior.
8. Confirm recovery through request rate, error rate, latency, readiness, and alert state.

Severity model:

- Critical: API unavailable, readiness failure, sustained high error ratio.
- Warning: elevated latency, dependency degradation, non-zero 5xx rate.
- Informational: isolated simulated errors during testing.

Severity matrix:

| Severity | Customer impact | Examples | Response |
| --- | --- | --- | --- |
| SEV1 | Broad outage or rapid SLO burn | API unavailable, fast-burn alert | Incident commander, mitigation first, frequent updates |
| SEV2 | Material partial degradation | dependency failures, high p95 latency | On-call owner, focused triage, rollback or isolate |
| SEV3 | Limited or intermittent issue | isolated route errors | Team triage, backlog corrective action |
| SEV4 | No active customer impact | dashboard gap, noisy alert | Planned improvement |

Recovery validation checklist:

- Alerts are resolved or understood.
- Error rate has returned below threshold.
- p95 latency is below target.
- Readiness and liveness checks are healthy.
- New logs no longer show the failing exception.
- Tempo traces show dependency spans returning successfully.
- Error budget burn rate has normalized.
