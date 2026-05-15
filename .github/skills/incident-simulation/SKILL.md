# Incident Simulation Skill

## Goal

Run controlled failure scenarios that produce useful metrics, logs, traces, and RCA evidence.

## Workflow

1. Start the stack and verify baseline smoke test.
2. Trigger one failure mode.
3. Capture Prometheus/Grafana/Loki/Tempo evidence.
4. Recover the stack and rerun smoke validation.

## Commands

```bash
bash .github/skills/incident-simulation/scripts/run-incident-simulation.sh dependency
bash scripts/simulate-errors.sh
bash scripts/simulate-latency.sh
```

## Validation

Always finish with:

```bash
bash scripts/smoke-test.sh
```

## Troubleshooting

If the stack cannot recover, run `docker compose down -v --remove-orphans` and restart with `docker compose up -d --build`.
