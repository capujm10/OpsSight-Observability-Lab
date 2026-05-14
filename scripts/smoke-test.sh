#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DEPENDENCY_URL="${DEPENDENCY_URL:-http://localhost:8081}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
LOKI_URL="${LOKI_URL:-http://localhost:3100}"
TEMPO_URL="${TEMPO_URL:-http://localhost:3200}"

echo "===== API health checks ====="
curl -fsS "${BASE_URL}/openapi.json" >/dev/null

echo "===== Dependency health ====="
curl -fsS "${DEPENDENCY_URL}/health/ready" >/dev/null

echo "===== Metrics validation ====="
curl -fsS "${BASE_URL}/metrics" | grep -q "opsight_http_requests_total"
curl -fsS "${DEPENDENCY_URL}/metrics" | grep -q "opsight_payment"

echo "===== Observability stack ====="
curl -fsS "${PROM_URL}/-/healthy" >/dev/null
curl -fsS "${LOKI_URL}/ready" >/dev/null
curl -fsS "${TEMPO_URL}/ready" >/dev/null

echo "===== Waiting for Grafana ====="
for i in {1..30}; do
  if curl -fsS "${GRAFANA_URL}/api/health" >/dev/null 2>&1; then
    echo "Grafana is ready"
    break
  fi

  echo "Waiting for Grafana... attempt $i/30"
  sleep 5

  if [ "$i" -eq 30 ]; then
    echo "Grafana did not become ready in time"
    exit 1
  fi
done

echo "===== Prometheus query ====="
curl -fsS "${PROM_URL}/api/v1/query?query=up" >/dev/null

echo "===== Orders endpoint ====="
curl -fsS "${BASE_URL}/api/v1/orders" >/dev/null

echo "Smoke test passed."