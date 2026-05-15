# Contributing

## Local Setup

Use Python 3.12 for service validation.

```bash
python -m pip install --upgrade pip
python -m pip install ruff==0.8.4 mypy==1.14.1 yamllint==1.35.1 pip-audit==2.9.0
python -m pip install -r apps/api/requirements.txt
python -m pip install -r apps/dependency/requirements.txt
python -m pip install -r apps/ai-rca/requirements.txt
python -m pip install -r apps/local-runtime-exporter/requirements.txt
```

Optional pre-commit setup:

```bash
python -m pip install pre-commit
pre-commit install
```

## Quality Gates

Run the same service-scoped checks used by CI:

```bash
make lint
make format-check
make typecheck
make test
make validate-compose
```

The API, dependency, and AI RCA services each use a service-local Python package named `app`. Run tests from each service directory to avoid import collisions.

Direct commands used by CI:

```bash
python -m ruff check apps scripts tests
python -m ruff format --check apps scripts tests
python -m mypy --no-incremental --config-file pyproject.toml apps/api/app
python -m mypy --no-incremental --config-file pyproject.toml apps/dependency/app
python -m mypy --no-incremental --config-file pyproject.toml apps/ai-rca/app
cd apps/api && python -m pytest
cd ../ai-rca && python -m pytest
cd ../..
python -m pytest tests
docker compose config --quiet
```

## Release Process

OpsSight uses semantic versioning for public portfolio milestones:

- `MAJOR`: architecture or runtime changes that materially alter how the lab is operated.
- `MINOR`: new dashboards, validation gates, runbooks, scenarios, or documentation packages.
- `PATCH`: dependency updates, bug fixes, formatting, and documentation corrections.

Before tagging a release:

1. Run local quality gates and smoke validation.
2. Confirm GitHub Actions CI and CodeQL pass.
3. Update `CHANGELOG.md`.
4. Tag with `vMAJOR.MINOR.PATCH`.
5. Keep release notes realistic about local-lab scope and production migration gaps.

## Pull Request Expectations

- Keep deterministic `rule_based` AI RCA behavior working without LLM access.
- Do not commit secrets, generated artifacts, local dashboards exports, or environment files.
- Update docs when changing ports, environment variables, telemetry labels, or API contracts.
- Keep CI gates and security scans at least as strict as the current workflow.
- Prefer focused changes over broad refactors.
