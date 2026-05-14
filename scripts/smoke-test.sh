#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DEPENDENCY_URL="${DEPENDENCY_URL:-http://localhost:8081}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
LOKI_URL="${LOKI_URL:-http://localhost:3100}"
TEMPO_URL="${TEMPO_URL:-http://localhost:3200}"

echo "===== API health checks ====="
curl -v "${BASE_URL}/api/v1/health/live"
curl -v "${BASE_URL}/api/v1/health/ready"

echo "===== Dependency health ====="
curl -v "${DEPENDENCY_URL}/health/ready"

echo "===== Metrics validation ====="
curl -v "${BASE_URL}/metrics" | grep "opsight_http_requests_total"
curl -v "${DEPENDENCY_URL}/metrics" | grep "opsight_payment"

echo "===== Observability stack ====="
curl -v "${PROM_URL}/-/healthy"
curl -v "${LOKI_URL}/ready"
curl -v "${TEMPO_URL}/ready"
curl -v "${GRAFANA_URL}/api/health"

echo "===== Prometheus query ====="
curl -v "${PROM_URL}/api/v1/query?query=up"

echo "===== OpenAPI routes ====="
curl -s "${BASE_URL}/openapi.json"

echo "===== Orders endpoint ====="
curl -v "${BASE_URL}/api/v1/orders"

echo "Smoke test passed: API, dependency service, metrics endpoints, Prometheus, Loki, Tempo, and Grafana are reachable."