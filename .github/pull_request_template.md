## Summary

- 

## Validation

- [ ] `python -m ruff check apps scripts tests`
- [ ] `python -m ruff format --check apps scripts tests`
- [ ] `python -m mypy --config-file pyproject.toml apps/api/app`
- [ ] `python -m mypy --config-file pyproject.toml apps/dependency/app`
- [ ] `python -m mypy --config-file pyproject.toml apps/ai-rca/app`
- [ ] `cd apps/api && python -m pytest`
- [ ] `cd apps/ai-rca && python -m pytest`
- [ ] `python -m pytest tests`
- [ ] `docker compose config --quiet`

## Dependency Governance

- [ ] Dependabot PRs keep grouped minor/patch updates together and leave major upgrades isolated for review
- [ ] Dependency changes include passing CI, pip-audit, and smoke-relevant validation when runtime behavior may change
- [ ] Security-sensitive dependency changes have been checked against `SECURITY.md` and `docs/security-hardening.md`

## Operational Impact

- [ ] No changes to public API contracts
- [ ] No changes to telemetry label names
- [ ] No new secrets, credentials, or internal URLs committed
- [ ] Documentation updated when behavior changed
