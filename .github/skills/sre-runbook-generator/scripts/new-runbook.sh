#!/usr/bin/env bash
set -euo pipefail

name="${1:?runbook name required}"
output="${2:?output path required}"

mkdir -p "$(dirname "${output}")"
sed "s/{{RUNBOOK_NAME}}/${name}/g" .github/skills/sre-runbook-generator/templates/runbook-template.md > "${output}"
echo "Created ${output}"
