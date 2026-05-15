#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${OUTPUT_DIR:-artifacts/demo-assets}"
mkdir -p "${OUTPUT_DIR}"

cat > "${OUTPUT_DIR}/capture-plan.md" <<'MARKDOWN'
# OpsSight Demo Asset Capture Plan

Capture real screenshots after the stack is running and at least one incident scenario has been generated.

## Required Views

- Grafana SRE Overview: http://localhost:3000
- Grafana API Golden Signals: http://localhost:3000
- Grafana Incident Investigation: http://localhost:3000
- Prometheus targets: http://localhost:9090/targets
- Prometheus alerts: http://localhost:9090/alerts
- Loki Explore filtered by `correlation_id`
- Tempo trace detail opened from a trace ID
- GitHub Actions CI and CodeQL workflow run pages

## Suggested Filenames

- `01-grafana-sre-overview.png`
- `02-api-golden-signals.png`
- `03-incident-investigation.png`
- `04-prometheus-targets.png`
- `05-loki-correlation-id.png`
- `06-tempo-trace-detail.png`
- `07-github-actions-ci.png`
- `08-codeql-workflow.png`
MARKDOWN

echo "Created ${OUTPUT_DIR}/capture-plan.md"
