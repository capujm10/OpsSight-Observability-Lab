# Smoke Test Failure Runbook

The smoke test validates that the local runtime is operational enough for demos, incident scenarios, and portfolio review.

## Validated Checks

- API OpenAPI endpoint
- dependency readiness
- API metrics endpoint
- dependency metrics endpoint
- Prometheus health
- Loki readiness
- Tempo readiness
- Grafana health
- Prometheus query API
- `/api/v1/orders`

## First Response

```bash
docker compose ps
bash scripts/smoke-test.sh
docker compose logs --tail=100
```

## Failure Mapping

| Failed Section | Likely Area | Next Check |
| --- | --- | --- |
| API health checks | API container, port conflict, startup failure | `docker compose logs api --tail=100` |
| Dependency health | payment gateway startup or healthcheck | `docker compose logs dependency --tail=100` |
| Metrics validation | instrumentation or route regression | `curl http://localhost:8000/metrics` |
| Observability stack | Prometheus, Loki, Tempo startup | backend-specific logs and readiness endpoint |
| Waiting for Grafana | Grafana provisioning or slow startup | `docker compose logs grafana --tail=100` |
| Prometheus query | Prometheus API or rules config | `curl http://localhost:9090/api/v1/query?query=up` |
| Orders endpoint | API route or dependency call path | API logs and dependency logs |

## Recovery Rules

- Keep the smoke test strict; do not bypass failed checks.
- Prefer increasing readiness wait loops only when startup is legitimately slow.
- Fix service health, telemetry endpoints, or Compose dependencies at the source.
- Capture the failing logs before running `docker compose down -v`.
