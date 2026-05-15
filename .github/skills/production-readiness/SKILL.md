# Production Readiness Skill

## Goal

Evaluate whether a change keeps OpsSight ready for public portfolio review and local operational validation.

## Workflow

1. Run static validation.
2. Run repository tests.
3. Validate Compose and Kubernetes manifests.
4. Run smoke test when the stack is available.
5. Document residual risks.

## Commands

```bash
bash .github/skills/production-readiness/scripts/run-readiness-check.sh
bash scripts/validate-all.sh
```

## Validation

Use `templates/readiness-checklist.md` for PR evidence.

## Troubleshooting

If Docker is unavailable, record the Docker engine error separately from repository validation failures.
