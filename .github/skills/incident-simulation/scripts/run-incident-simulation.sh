#!/usr/bin/env bash
set -euo pipefail

scenario="${1:-dependency}"
echo "== Running incident simulation: ${scenario} =="

case "${scenario}" in
  dependency)
    curl -fsS http://localhost:8000/api/v1/simulate/dependency-failure || true
    ;;
  errors)
    bash scripts/simulate-errors.sh
    ;;
  latency)
    bash scripts/simulate-latency.sh
    ;;
  *)
    echo "Unknown scenario: ${scenario}" >&2
    exit 2
    ;;
esac

echo "Validate with Grafana, Prometheus, Loki, Tempo, and bash scripts/smoke-test.sh"
