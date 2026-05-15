# Dependency Outage Example

Run:

```bash
bash .github/skills/incident-simulation/scripts/run-incident-simulation.sh dependency
```

Expected evidence:

- API logs show dependency failure.
- Prometheus request/error metrics change.
- Grafana API Golden Signals reflects degraded path.
