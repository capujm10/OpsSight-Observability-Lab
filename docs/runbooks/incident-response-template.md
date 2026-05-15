# Incident Response Template

## Incident Summary

- Incident ID:
- Severity:
- Status: investigating | mitigated | resolved
- Start time:
- Detection source: alert | smoke test | dashboard | user report
- Affected service(s):
- Customer or demo impact:

## Initial Triage

1. Confirm the symptom in Grafana or Prometheus.
2. Check service readiness endpoints.
3. Identify whether the issue affects API, dependency, telemetry backend, or dashboard availability.
4. Capture current alerts, recent logs, and representative trace IDs.

## Evidence

| Signal | Query or Source | Finding |
| --- | --- | --- |
| Metrics |  |  |
| Logs |  |  |
| Traces |  |  |
| Runtime | `docker compose ps` |  |
| CI | GitHub Actions run |  |

## Mitigation

- Immediate action:
- Owner:
- Expected validation:
- Rollback or stop condition:

## Communication

- Internal update cadence:
- Current user-facing status:
- Next update:

## Resolution Criteria

- Readiness endpoints are healthy.
- Smoke test passes.
- Error rate and latency return to expected local baseline.
- Logs stop showing the triggering error pattern.
- Related traces show dependency recovery.

## Follow-Up

- Root cause:
- Contributing factors:
- Preventive action:
- Documentation updates:
- CI or alerting updates:
