#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
COUNT="${COUNT:-12}"

for i in $(seq 1 "$COUNT"); do
  curl -sS -o /dev/null -w "latency-scenario-${i} status=%{http_code} duration=%{time_total}s\n" \
    -H "x-correlation-id: latency-scenario-${i}" \
    "${BASE_URL}/api/v1/simulate/latency" &
  sleep 0.3
done
wait
