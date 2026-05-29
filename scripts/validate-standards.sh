#!/usr/bin/env bash
set -euo pipefail

failures=0

require_file() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo "MISSING FILE: $file"
    failures=$((failures + 1))
  fi
}

require_pattern() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if ! grep -Eq "$pattern" "$file"; then
    echo "MISSING PATTERN: $label ($file)"
    failures=$((failures + 1))
  fi
}

echo "Validating governance and observability standards context..."

require_file "governance.yml"
require_file "governance.context.md"
require_file "observability.context.md"
require_file "README.md"
require_file "docs/opsight-case-study.md"

require_pattern "governance.yml" "^repository:" "repository section"
require_pattern "governance.yml" "^  purpose:" "repository purpose"
require_pattern "governance.yml" "^  maturity_level:" "maturity level"
require_pattern "governance.yml" "^  operational_mode:" "operational mode"
require_pattern "governance.yml" "^  strategic_role:" "strategic role"
require_pattern "governance.yml" "^risk_profile:" "risk profile"
require_pattern "governance.yml" "^standards_alignment:" "standards alignment"
require_pattern "governance.yml" "^validation_requirements:" "validation requirements"

require_pattern "governance.context.md" "^## Relationship to Engineering Standards" "engineering-standards relationship"
require_pattern "governance.context.md" "^## Governance Philosophy" "governance philosophy"
require_pattern "governance.context.md" "^## Repository Boundaries" "repository boundaries"
require_pattern "governance.context.md" "^## Documentation Expectations" "documentation expectations"

require_pattern "observability.context.md" "^## Telemetry Concepts" "telemetry concepts"
require_pattern "observability.context.md" "^## Monitoring Philosophy" "monitoring philosophy"
require_pattern "observability.context.md" "^## Observability Architecture" "observability architecture"
require_pattern "observability.context.md" "^## Recruiter-Facing Engineering Value" "recruiter-facing value"

require_pattern "README.md" "^## Observability Platform Archetype" "README archetype section"
require_pattern "README.md" "governance\\.yml" "README governance link"
require_pattern "README.md" "observability\\.context\\.md" "README observability context link"
require_pattern "README.md" "docs/opsight-case-study\\.md" "README case study link"

if [ "$failures" -ne 0 ]; then
  echo "Standards validation failed with $failures issue(s)."
  exit 1
fi

echo "Standards validation passed."
