# Project Profile

## Purpose
OpsSight is a local-first observability engineering lab for SRE, DevSecOps, OpenTelemetry, CI/CD hardening, incident simulation, AI-assisted RCA, and production-readiness validation.

## Stack
- FastAPI services.
- Docker Compose local runtime.
- Kubernetes manifests with Kustomize readiness artifacts.
- Grafana, Prometheus, Loki, Tempo, Grafana Alloy, and OpenTelemetry.

## Important paths
- `AGENTS.md`: repository-wide AI agent rules.
- `README.md`: project overview, quickstart, architecture, validation, and operational baseline.
- `.github/copilot-instructions.md`: concise AI coding guidance that complements `AGENTS.md`.
- `docs/`: canonical architecture, operations, runbooks, incident, security, SLO, and AI RCA documentation.
- `apps/`: API, dependency, AI RCA, and local runtime exporter services.
- `observability/`: Grafana, Prometheus, Loki, Tempo, and Alloy configuration.
- `k8s/`: Kubernetes readiness manifests and overlays.
- `scripts/`: validation, smoke-test, incident, RCA, and operations helpers.

## Active goals
- Preserve realistic enterprise-style observability and operational maturity.
- Keep local runtime behavior reproducible and smoke-testable.
- Preserve deterministic AI RCA fallback when external LLM providers are unavailable.
- Keep changes small, reversible, reviewable, and production-oriented.

## Related Obsidian memory areas
- None required for baseline repository work.

## Retrieval policy
- Use `.ai-context/retrieval-policy.md`.
- Prefer canonical repository docs over external or memory sources unless the user explicitly asks otherwise.

## Safety notes
- Docker Compose is the full local runtime; Kubernetes and Helm are readiness/migration artifacts unless a deployment path is explicitly added.
- Do not expose local demo credentials outside trusted local use.
- Do not change metric names, labels, alert names, dashboard assumptions, smoke-test expectations, or CI gates without explicit scope and validation.
