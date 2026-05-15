#!/usr/bin/env bash
set -euo pipefail

echo "== OpsSight observability audit =="
docker compose ps
bash scripts/observability-check.sh
echo "Audit checks completed. Use .github/skills/observability-audit/templates/observability-audit-report.md for findings."
