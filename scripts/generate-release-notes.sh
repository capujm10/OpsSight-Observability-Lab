#!/usr/bin/env bash
set -euo pipefail

CHANGELOG="${CHANGELOG:-CHANGELOG.md}"
OUTPUT="${OUTPUT:-}"

if [ ! -f "${CHANGELOG}" ]; then
  echo "Missing ${CHANGELOG}" >&2
  exit 1
fi

notes="$(awk '
  /^## \[/ {
    if (seen) {
      exit
    }
    seen=1
  }
  seen {
    print
  }
' "${CHANGELOG}")"

if [ -z "${notes}" ]; then
  echo "No release section found in ${CHANGELOG}" >&2
  exit 1
fi

if [ -n "${OUTPUT}" ]; then
  printf "%s\n" "${notes}" > "${OUTPUT}"
  echo "Wrote ${OUTPUT}"
else
  printf "%s\n" "${notes}"
fi
