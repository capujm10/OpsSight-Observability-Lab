#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DEPENDENCY_URL="${DEPENDENCY_URL:-http://localhost:8081}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
TEMPO_URL="${TEMPO_URL:-http://localhost:3200}"

log() {
  printf "\n== %s ==\n" "$1"
}

check_contains() {
  local label="$1"
  local needle="$2"
  shift 2
  log "${label}"
  "$@" | grep -q "${needle}"
}

tmp_headers="$(mktemp)"
trap 'rm -f "${tmp_headers}"' EXIT

log "API availability"
curl -fsS "${BASE_URL}/health/ready" >/dev/null

log "Dependency health"
curl -fsS "${DEPENDENCY_URL}/health/ready" >/dev/null

check_contains "API metrics endpoint" "opsight_http_requests_total" curl -fsS "${BASE_URL}/metrics"
check_contains "Dependency metrics endpoint" "opsight_payment_requests_total" curl -fsS "${DEPENDENCY_URL}/metrics"

log "Trace generation"
curl -fsS -D "${tmp_headers}" -H "x-correlation-id: synthetic-trace-validation" "${BASE_URL}/api/v1/orders" >/dev/null
trace_id="$(awk 'tolower($1) == "x-trace-id:" {print $2}' "${tmp_headers}" | tr -d '\r' | tail -n 1)"
if [ -z "${trace_id}" ] || [ "${trace_id}" = "-" ]; then
  echo "API did not return a usable x-trace-id header" >&2
  exit 1
fi

log "Prometheus synthetic query"
prometheus_result="$(curl -fsSG --data-urlencode 'query=up{job="opsight-api"}' "${PROM_URL}/api/v1/query")"
printf "%s" "${prometheus_result}" | grep -q '"status":"success"'
printf "%s" "${prometheus_result}" | grep -Fq '"result":[{"metric":'

log "Tempo readiness"
curl -fsS "${TEMPO_URL}/ready" >/dev/null

echo "Synthetic monitoring passed. trace_id=${trace_id}"
