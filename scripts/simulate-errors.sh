#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
COUNT="${COUNT:-30}"

for i in $(seq 1 "$COUNT"); do
  curl -sS -o /dev/null -w "error-scenario-${i} status=%{http_code}\n" \
    -H "x-correlation-id: error-scenario-${i}" \
    "${BASE_URL}/api/v1/simulate/error" || true
  sleep 0.2
done
