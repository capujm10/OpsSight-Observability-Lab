#!/usr/bin/env bash
set -euo pipefail

incident_id="${1:?incident id required}"
output="${2:?output path required}"

mkdir -p "$(dirname "${output}")"
sed "s/{{INCIDENT_ID}}/${incident_id}/g" .github/skills/postmortem-generator/templates/postmortem-template.md > "${output}"
echo "Created ${output}"
