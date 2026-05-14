# Production Readiness Audit

Audit date: 2026-05-14

## Executive Report

OpsSight Observability Lab is close to public portfolio readiness after the hardening pass. The repository now has split CI gates, deterministic service-scoped tests, non-root custom containers, security headers, public-maintainer files, dependency scanning, and documented local-only risk boundaries.

Readiness score:

- Before: 68/100
- Target after validation: 90+/100

Primary release blockers addressed:

- CI failed at Ruff before running deeper gates.
- Formatting drift was not enforced.
- Mixed repo-level pytest collection could import the wrong service-local `app` package.
- Local runtime exporter container ran as root.
- Public maintainer files and security reporting guidance were missing.

## Technical Findings

Critical:

- Ruff failures blocked the latest GitHub Actions runs. The fix is to format code, sort imports, and split long RCA strings without changing RCA output semantics.

High:

- Service-local packages named `app` collide in a single Python import context. The repository keeps that structure intentionally, and CI now runs tests from each service directory.
- The previous CI workflow was a single linear job. Split gates now isolate lint, typecheck, tests, infrastructure validation, security, Docker build, and smoke test failures.

Medium:

- Broad exception handling existed in telemetry collectors. Runtime exporter degradation paths now log concrete reasons where safe.
- Pydantic settings and request models had limited bounds. Low-risk numeric bounds and request-body extra-field rejection were added for API-facing payloads.

Low:

- Public contribution, security, ownership, and issue/PR templates were missing.
- README needed clearer local-demo credential warnings and service-scoped test guidance.

## Security Findings

- No committed real secrets were found by targeted pattern scan.
- Grafana `admin` / `admin` is retained only as a local-demo default through environment-variable fallbacks.
- Docker socket and host filesystem mounts are high risk and must not be carried into production deployments.
- Custom application containers should remain non-root with dropped capabilities and no-new-privileges.
- Python dependency auditing is now part of CI. Container filesystem scanning is included as a non-blocking signal because scanner databases and unfixed base-image findings can be noisy.

## CI/CD Findings

- The workflow now uses least-privilege `contents: read` permissions and concurrency cancellation.
- Ruff lint and format checks run before slower gates.
- Tests run in service-local contexts to avoid `app` import collisions.
- Infrastructure validation covers YAML, Docker Compose config, and Kubernetes dry-run manifests.
- Docker build and stack smoke tests are separated from unit and static checks.

## Roadmap

- Add authentication and authorization before exposing API or AI RCA endpoints outside a trusted local workstation.
- Add SBOM generation and signed image provenance for release builds.
- Add real Alertmanager notification delivery examples for a non-local environment.
- Add screenshot QA for Grafana dashboards after dashboard or Grafana version changes.
- Add production Helm values for external secrets, persistent storage classes, ingress TLS, and managed telemetry backends.

## Publication Checklist

- [x] MIT license present.
- [x] README has quickstart, architecture, tests, CI, and security baseline.
- [x] Security policy present.
- [x] Contribution guide present.
- [x] CODEOWNERS present.
- [x] Dependabot configured.
- [x] Issue and PR templates present.
- [x] `.env` and generated artifacts ignored.
- [x] Local-only credentials documented.
- [x] CI includes lint, format, typecheck, tests, infra validation, dependency audit, Docker build, and smoke test.
- [ ] Add real screenshots before a polished public launch.
- [ ] Re-run GitHub Actions after pushing this branch.
