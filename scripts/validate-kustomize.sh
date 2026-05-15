#!/usr/bin/env bash
set -euo pipefail

OVERLAYS=(local dev staging prod)

log() {
  printf "\n== %s ==\n" "$1"
}

run() {
  printf "+ %s\n" "$*"
  "$@"
}

for overlay in "${OVERLAYS[@]}"; do
  path="k8s/overlays/${overlay}"
  log "Render Kustomize overlay: ${overlay}"
  run kubectl kustomize "${path}" >/dev/null

  log "Dry-run Kustomize overlay: ${overlay}"
  run kubectl apply --dry-run=client --validate=false -k "${path}"
done

log "Kustomize validation completed"
