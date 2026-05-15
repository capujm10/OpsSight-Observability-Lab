#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DEPENDENCY_URL="${DEPENDENCY_URL:-http://localhost:8081}"
AI_RCA_URL="${AI_RCA_URL:-http://localhost:8090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
LOKI_URL="${LOKI_URL:-http://localhost:3100}"
TEMPO_URL="${TEMPO_URL:-http://localhost:3200}"
PROM_TARGET_TIMEOUT_SECONDS="${PROM_TARGET_TIMEOUT_SECONDS:-90}"

check() {
  local label="$1"
  shift
  printf "== %s ==\n" "${label}"
  "$@"
}

contains() {
  local label="$1"
  local needle="$2"
  shift 2
  printf "== %s ==\n" "${label}"
  "$@" | grep -q "${needle}"
}

prometheus_job_is_up() {
  local job="$1"
  local response
  response="$(curl -fsSG --data-urlencode "query=up{job=\"${job}\"} == 1" "${PROM_URL}/api/v1/query")"
  ! grep -q '"result":\[\]' <<<"${response}"
}

wait_for_prometheus_job() {
  local job="$1"
  local deadline=$((SECONDS + PROM_TARGET_TIMEOUT_SECONDS))

  printf "== Prometheus target: %s ==\n" "${job}"
  until prometheus_job_is_up "${job}"; do
    if [ "${SECONDS}" -ge "${deadline}" ]; then
      echo "Prometheus job did not become up before timeout: ${job}" >&2
      curl -fsS "${PROM_URL}/api/v1/targets" >&2 || true
      exit 1
    fi
    sleep 3
  done
}

check "API readiness" curl -fsS "${BASE_URL}/health/ready"
check "Dependency readiness" curl -fsS "${DEPENDENCY_URL}/health/ready"
check "AI RCA readiness" curl -fsS "${AI_RCA_URL}/health/ready"

contains "API metrics" "opsight_http_requests_total" curl -fsS "${BASE_URL}/metrics"
contains "Dependency metrics" "opsight_payment" curl -fsS "${DEPENDENCY_URL}/metrics"
contains "AI RCA metrics" "opsight_ai_rca" curl -fsS "${AI_RCA_URL}/metrics"

check "Prometheus health" curl -fsS "${PROM_URL}/-/healthy"
check "Prometheus targets" curl -fsS "${PROM_URL}/api/v1/targets"
check "Prometheus up query" curl -fsS "${PROM_URL}/api/v1/query?query=up"
for job in prometheus opsight-api payment-gateway opsight-ai-rca local-runtime-exporter alloy grafana; do
  wait_for_prometheus_job "${job}"
done

check "Loki readiness" curl -fsS "${LOKI_URL}/ready"
check "Tempo readiness" curl -fsS "${TEMPO_URL}/ready"
check "Grafana readiness" curl -fsS "${GRAFANA_URL}/api/health"

tmp_headers="$(mktemp)"
trap 'rm -f "${tmp_headers}"' EXIT

check "Trace header validation" curl -fsS -D "${tmp_headers}" -H "x-correlation-id: opsight-observability-check" "${BASE_URL}/api/v1/orders"
grep -qi "^x-trace-id:" "${tmp_headers}"
grep -qi "^x-correlation-id:" "${tmp_headers}"

echo "Observability check passed."
