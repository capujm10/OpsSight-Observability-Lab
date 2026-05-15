#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
SCENARIO="${1:-all}"
COUNT="${COUNT:-20}"

usage() {
  cat <<'USAGE'
Usage: bash scripts/simulate-incident.sh [scenario]

Scenarios:
  dependency-outage      Force payment-gateway failures through the API.
  latency-spike          Generate high-latency API and dependency spans.
  elevated-error-rate    Generate API 500 responses.
  degraded-upstream      Mix successful traffic with slow/failing upstream calls.
  all                    Run all scenarios in sequence.
USAGE
}

request() {
  local name="$1"
  local path="$2"
  local count="$3"

  for i in $(seq 1 "${count}"); do
    curl -sS --connect-timeout 5 --max-time 15 -o /dev/null -w "${name}-${i} status=%{http_code} duration=%{time_total}s\n" \
      -H "x-correlation-id: ${name}-${i}" \
      "${BASE_URL}${path}"
    sleep 0.2
  done
}

baseline() {
  request "baseline-orders" "/api/v1/orders" 5
}

dependency_outage() {
  request "dependency-outage" "/api/v1/simulate/dependency-failure" "${COUNT}"
}

latency_spike() {
  request "latency-spike" "/api/v1/simulate/latency" "${COUNT}"
}

elevated_error_rate() {
  request "elevated-error-rate" "/api/v1/simulate/error" "${COUNT}"
}

degraded_upstream() {
  local half=$((COUNT / 2))
  [ "${half}" -lt 1 ] && half=1
  request "degraded-upstream-slow" "/api/v1/simulate/latency" "${half}"
  request "degraded-upstream-fail" "/api/v1/simulate/dependency-failure" "${half}"
}

case "${SCENARIO}" in
  dependency-outage)
    dependency_outage
    ;;
  latency-spike)
    latency_spike
    ;;
  elevated-error-rate)
    elevated_error_rate
    ;;
  degraded-upstream)
    degraded_upstream
    ;;
  all)
    baseline
    latency_spike
    elevated_error_rate
    dependency_outage
    degraded_upstream
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

echo "Incident simulation completed: ${SCENARIO}"
