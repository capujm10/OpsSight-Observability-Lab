#!/usr/bin/env bash
set -euo pipefail

REQUIRE_TRIVY="${REQUIRE_TRIVY:-0}"
PYTHON_BIN="${PYTHON_BIN:-}"
REQ_FILES=(
  "apps/api/requirements.txt"
  "apps/dependency/requirements.txt"
  "apps/ai-rca/requirements.txt"
  "apps/local-runtime-exporter/requirements.txt"
)

log() {
  printf "\n== %s ==\n" "$1"
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

resolve_python

log "Python dependency audit"
for req in "${REQ_FILES[@]}"; do
  echo "+ ${PYTHON_BIN} -m pip_audit -r ${req}"
  "${PYTHON_BIN}" -m pip_audit -r "${req}"
done

log "Secret pattern scan"
if rg --version >/dev/null 2>&1; then
  if rg -n --hidden --glob '!.git/**' --glob '!artifacts/**' --glob '!*.md' \
    "(AKIA|BEGIN RSA|BEGIN OPENSSH|github_pat|ghp_|password\\s*=|api[_-]?key\\s*=|secret\\s*=)" .; then
    echo "Potential secret-like strings found. Review output above." >&2
    exit 1
  fi
else
  echo "ripgrep not available; skipping secret pattern scan"
fi

log "Trivy filesystem scan"
if command -v trivy >/dev/null 2>&1; then
  trivy fs --severity CRITICAL,HIGH --ignore-unfixed .
elif [ "${REQUIRE_TRIVY}" = "1" ]; then
  echo "Trivy is required but not installed" >&2
  exit 1
else
  echo "Trivy not installed; CI runs Trivy through GitHub Actions"
fi

log "Security audit completed"
