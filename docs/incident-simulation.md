# Incident Simulation

Incident simulations create observable, reversible failure signals for Prometheus, Grafana, Loki, and Tempo. They are intended for local demos, runbook practice, and AI RCA evidence generation.

## Script

Run all scenarios:

```bash
bash scripts/simulate-incident.sh all
```

Run a focused scenario:

```bash
bash scripts/simulate-incident.sh dependency-outage
bash scripts/simulate-incident.sh latency-spike
bash scripts/simulate-incident.sh elevated-error-rate
bash scripts/simulate-incident.sh degraded-upstream
```

Make targets:

```bash
make incident-sim
make dependency-outage
make degraded-upstream
make latency
make errors
```

## Scenarios

| Scenario | Signal produced | Primary telemetry |
| --- | --- | --- |
| `dependency-outage` | Forced payment-gateway failures through the API | API 5xx, dependency failure counter, warning/error logs, failed dependency spans |
| `latency-spike` | Slow API and dependency requests | API p95 latency, dependency p95 latency, slow spans |
| `elevated-error-rate` | Repeated API exception path | API 5xx rate, Loki error logs, burn-rate pressure |
| `degraded-upstream` | Mixed slow and failing upstream responses | dependency latency, dependency failures, API error ratio |

## Recommended Demo Flow

1. Start the stack with `docker compose up -d --build`.
2. Run `bash scripts/smoke-test.sh`.
3. Generate baseline traffic with `make load`.
4. Run one incident scenario.
5. Open Grafana dashboards:
   - `OpsSight SLO Operational Maturity`
   - `OpsSight API Golden Signals`
   - `OpsSight Incident Investigation`
6. Inspect Prometheus alerts and Loki logs.
7. Use Tempo traces from returned `x-trace-id` values or dashboard links.
8. Run `make synthetic-monitor` after recovery.

## Safety

The scenarios call local API simulation endpoints only. They do not change service configuration, mutate secrets, or require privileged host access. Stop the stack with:

```bash
docker compose down -v --remove-orphans
```
