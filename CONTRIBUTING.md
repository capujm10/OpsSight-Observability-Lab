# Contributing

## Local Setup

Use Python 3.12 for service validation.

```bash
python -m pip install --upgrade pip
python -m pip install ruff==0.8.4 mypy==1.14.1 yamllint==1.35.1 pip-audit==2.9.0
python -m pip install -r apps/api/requirements.txt
python -m pip install -r apps/dependency/requirements.txt
python -m pip install -r apps/ai-rca/requirements.txt
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

## Pull Request Expectations

- Keep deterministic `rule_based` AI RCA behavior working without LLM access.
- Do not commit secrets, generated artifacts, local dashboards exports, or environment files.
- Update docs when changing ports, environment variables, telemetry labels, or API contracts.
- Prefer focused changes over broad refactors.
