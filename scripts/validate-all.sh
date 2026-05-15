#!/usr/bin/env bash
set -euo pipefail

RUN_SMOKE="${RUN_SMOKE:-1}"
START_STACK="${START_STACK:-0}"
CLEANUP_STACK="${CLEANUP_STACK:-0}"
PYTHON_BIN="${PYTHON_BIN:-}"

log() {
  printf "\n== %s ==\n" "$1"
}

run() {
  printf "+ %s\n" "$*"
  "$@"
}

resolve_python() {
  if [ -n "${PYTHON_BIN}" ]; then
    return 0
  fi

  for candidate in python python.exe python3 py; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      PYTHON_BIN="${candidate}"
      return 0
    fi
  done

  echo "No Python interpreter found. Set PYTHON_BIN to the interpreter command." >&2
  exit 1
}

cleanup() {
  if [ "${START_STACK}" = "1" ] && [ "${CLEANUP_STACK}" = "1" ]; then
    docker compose down -v --remove-orphans
  fi
}

trap cleanup EXIT
resolve_python

log "Ruff lint"
run "${PYTHON_BIN}" -m ruff check apps scripts tests

log "Ruff format check"
run "${PYTHON_BIN}" -m ruff format --check apps scripts tests

log "Repository tests"
run "${PYTHON_BIN}" -m pytest tests

log "Docker Compose config"
run docker compose config --quiet

log "Kubernetes manifest dry-run"
run kubectl apply --dry-run=client --validate=false -f k8s/base -f k8s/api -f k8s/monitoring

if [ "${START_STACK}" = "1" ]; then
  log "Docker Compose build and start"
  run docker compose up -d --build
  run docker compose ps
fi

if [ "${RUN_SMOKE}" = "1" ]; then
  log "Smoke test"
  run bash scripts/smoke-test.sh
else
  log "Smoke test skipped"
  echo "RUN_SMOKE=0"
fi

log "Validation completed"
