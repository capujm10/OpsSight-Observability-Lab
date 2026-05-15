# Create Runbook Prompt

Create a production-style SRE runbook for this repository.

Requirements:

- Use OpsSight terminology and real services: `api`, `dependency`, `ai-rca`, `local-runtime-exporter`, Prometheus, Grafana, Loki, Tempo, and Alloy.
- Include detection signals, triage commands, decision tree, mitigation, validation, rollback, and escalation.
- Use concrete commands that work in this repo.
- Include smoke test and telemetry validation.
- Do not invent unsupported production infrastructure.

Validation commands to include when relevant:

```bash
docker compose ps
docker compose logs --tail=100
bash scripts/smoke-test.sh
curl -fsS http://localhost:9090/-/healthy
curl -fsS http://localhost:3100/ready
curl -fsS http://localhost:3200/ready
```
