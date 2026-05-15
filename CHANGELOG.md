# Changelog

This project follows semantic versioning for public portfolio milestones: `MAJOR.MINOR.PATCH`.

- `MAJOR`: significant architecture, runtime, or public interface changes.
- `MINOR`: new observability workflows, documentation artifacts, dashboards, or validation gates.
- `PATCH`: bug fixes, documentation corrections, dependency updates, and small hardening improvements.

## [1.0.0] - 2026-05-14

### Added

- Split GitHub Actions quality gates for linting, formatting, type checking, tests, infrastructure validation, security scanning, Docker builds, and smoke testing.
- CodeQL workflow for Python static analysis.
- KIND-backed Kubernetes dry-run validation.
- Docker Compose runtime validation and smoke test stabilization.
- Prometheus, Grafana, Loki, Tempo, Grafana Alloy, and OpenTelemetry documentation.
- SRE runbooks, incident response template, and sample postmortem.
- Production-readiness audit, security policy, contribution guide, CODEOWNERS, PR template, issue templates, and Dependabot configuration.

### Security

- Added `pip-audit` dependency scanning.
- Added Trivy filesystem scanning.
- Documented local-only credentials, Docker socket risk, and host filesystem mount boundaries.
- Confirmed repository-level secret scanning, push protection, and branch protection.

### Notes

- The stack remains a local-first observability lab, not a turnkey internet-facing production platform.
