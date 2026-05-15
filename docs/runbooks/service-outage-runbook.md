# Service Outage Runbook

Use this runbook when the API, dependency service, or AI RCA service fails readiness, disappears from Prometheus targets, or causes the smoke test to fail.

## Scope

- `api` on port `8000`
- `dependency` on port `8081`
- `ai-rca` on port `8090`
- Required observability backends: Prometheus, Loki, Tempo, Grafana

## Triage Commands

```bash
docker compose ps
docker compose logs api --tail=100
docker compose logs dependency --tail=100
docker compose logs ai-rca --tail=100
curl -fsS http://localhost:8000/health/ready
curl -fsS http://localhost:8081/health/ready
curl -fsS http://localhost:8090/health/ready
```

## Decision Tree

1. If a service is `unhealthy`, inspect its logs first.
2. If logs show dependency connection failures, confirm the downstream container is healthy.
3. If telemetry export errors appear but readiness is healthy, treat it as observability degradation rather than service outage.
4. If the API is healthy but smoke test fails on metrics, inspect `/metrics` output and Prometheus target state.
5. If Grafana is slow to become ready, wait for its health endpoint and inspect provisioning logs.

## Common Causes

- Downstream dependency is not healthy when API starts.
- Port conflict with a previous local process.
- Read-only container filesystem blocks an unexpected write path.
- Prometheus, Loki, or Tempo still starting when smoke checks begin.
- Docker Desktop resource pressure or stale volumes.

## Recovery

```bash
docker compose down -v --remove-orphans
docker compose up -d --build
bash scripts/smoke-test.sh
```

Do not remove smoke checks to recover a failing run. Fix the readiness, dependency, or telemetry cause.
