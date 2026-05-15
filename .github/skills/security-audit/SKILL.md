# Security Audit Skill

## Goal

Review dependency, container, workflow, and repository-governance security controls without weakening existing gates.

## Workflow

1. Run dependency and filesystem checks.
2. Inspect GitHub Actions and CodeQL workflow state.
3. Review Docker and Kubernetes security boundaries.
4. Produce findings with actionable remediation.

## Commands

```bash
bash .github/skills/security-audit/scripts/run-security-audit.sh
bash scripts/security-audit.sh
```

## Validation

- `python -m ruff check apps scripts tests`
- `docker compose config --quiet`
- `kubectl apply --dry-run=client --validate=false -f k8s/base -f k8s/api -f k8s/monitoring`

## Troubleshooting

If `pip-audit` is missing, install `pip-audit==2.9.0` in the active Python environment.
