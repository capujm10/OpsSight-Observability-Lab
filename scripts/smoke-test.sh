#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DEPENDENCY_URL="${DEPENDENCY_URL:-http://localhost:8081}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
LOKI_URL="${LOKI_URL:-http://localhost:3100}"
TEMPO_URL="${TEMPO_URL:-http://localhost:3200}"

curl -fsS "${BASE_URL}/api/v1/health/live" >/dev/null
curl -fsS "${BASE_URL}/api/v1/health/ready" >/dev/null
curl -fsS "${DEPENDENCY_URL}/health/ready" >/dev/null
curl -fsS "${BASE_URL}/metrics" | grep -q "opsight_http_requests_total"
curl -fsS "${DEPENDENCY_URL}/metrics" | grep -q "opsight_payment"
curl -fsS "${PROM_URL}/-/healthy" >/dev/null
curl -fsS "${LOKI_URL}/ready" >/dev/null
curl -fsS "${TEMPO_URL}/ready" >/dev/null
curl -fsS "${GRAFANA_URL}/api/health" >/dev/null

curl -fsS "${PROM_URL}/api/v1/query?query=up" >/dev/null
curl -fsS "${BASE_URL}/api/v1/orders" >/dev/null

echo "Smoke test passed: API, dependency service, metrics endpoints, Prometheus, Loki, Tempo, and Grafana are reachable."
