#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
COUNT="${COUNT:-120}"

for i in $(seq 1 "$COUNT"); do
  curl -sS -H "x-correlation-id: load-${i}" "${BASE_URL}/api/v1/orders" >/dev/null &
  if (( i % 10 == 0 )); then
    curl -sS -H "content-type: application/json" -H "x-correlation-id: create-${i}" \
      -d "{\"customer_id\":\"cust-load-${i}\",\"amount\":$((100 + i))}" \
      "${BASE_URL}/api/v1/orders" >/dev/null &
  fi
  sleep 0.1
done
wait
echo "Generated ${COUNT} baseline API requests."
