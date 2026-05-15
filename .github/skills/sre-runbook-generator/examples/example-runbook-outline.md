# Example Runbook Outline

- Scope: API readiness failure
- Detection: smoke test fails during API health checks
- Triage: `docker compose logs api --tail=100`
- Validation: `bash scripts/smoke-test.sh`
