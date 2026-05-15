# Security Policy

## Supported Scope

OpsSight Observability Lab is a local-first observability and SRE lab. The Docker Compose stack is intended for local demos, engineering practice, and portfolio review. It is not a hardened internet-facing deployment as shipped.

## Reporting A Vulnerability

Please report suspected vulnerabilities privately through GitHub Security Advisories when this repository is public. Include:

- affected component or path
- reproduction steps
- observed impact
- relevant logs, payloads, or screenshots

Do not open public issues for exploitable vulnerabilities.

## Local Demo Security Notes

- Grafana defaults to `admin` / `admin` only for local demo convenience. Set `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` before sharing or exposing the stack.
- Docker socket and host filesystem mounts are local observability features. Do not use those mounts in production.
- Kubernetes manifests use placeholders for secrets. Replace them with External Secrets, Sealed Secrets, or a cloud secret manager.
- AI provider API keys must be supplied through environment variables or secret managers and must not be committed.

## Current Security Controls

- GitHub secret scanning is enabled.
- GitHub push protection is enabled.
- `main` is protected and requires the repository CI checks before merge.
- CI runs `pip-audit` against Python requirement files.
- CI runs Trivy filesystem scanning for high and critical findings.
- CodeQL runs Python static analysis through GitHub code scanning.
- Dependabot is configured for version-update pull requests for GitHub Actions and Python requirements.
- Custom application containers run as non-root users and use conservative Compose runtime restrictions where compatible.

Dependabot security updates are not currently enabled in repository settings. Treat Dependabot here as version governance, not as a complete vulnerability-management program.

## Maintainer Checks

Before publishing changes, run:

```bash
python -m ruff check apps scripts tests
python -m ruff format --check apps scripts tests
python -m pytest tests
cd apps/api && python -m pytest
cd ../ai-rca && python -m pytest
cd ../..
docker compose config --quiet
```
