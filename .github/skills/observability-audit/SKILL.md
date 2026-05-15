# Observability Audit Skill

## Goal

Assess whether OpsSight telemetry is complete, actionable, and still aligned with SRE investigation workflows.

## Workflow

1. Inspect service health endpoints and `/metrics`.
2. Validate Prometheus, Loki, Tempo, and Grafana readiness.
3. Review dashboard, alert, and runbook coverage.
4. Capture findings using `templates/observability-audit-report.md`.

## Commands

```bash
bash .github/skills/observability-audit/scripts/run-observability-audit.sh
bash scripts/observability-check.sh
```

## Validation

- `docker compose config --quiet`
- `bash scripts/smoke-test.sh`
- `curl -fsS http://localhost:9090/api/v1/targets`

## Troubleshooting

If checks fail, run `docker compose ps` and inspect logs for the failed backend before changing dashboards or rules.
