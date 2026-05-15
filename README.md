# OpsSight Observability Lab

[![CI](https://github.com/capujm10/OpsSight-Observability-Lab/actions/workflows/ci.yml/badge.svg)](https://github.com/capujm10/OpsSight-Observability-Lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/capujm10/OpsSight-Observability-Lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/capujm10/OpsSight-Observability-Lab/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](pyproject.toml)
[![FastAPI](https://img.shields.io/badge/FastAPI-service%20mesh-009688.svg)](apps/api)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-local%20runtime-2496ED.svg)](docker-compose.yml)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-manifest%20validation-326CE5.svg)](k8s)
[![Prometheus](https://img.shields.io/badge/Prometheus-metrics%20%26%20alerts-E6522C.svg)](observability/prometheus)
[![Grafana](https://img.shields.io/badge/Grafana-dashboards-F46800.svg)](observability/grafana)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-traces%20via%20Alloy-000000.svg)](observability/alloy)

## Executive Summary

OpsSight Observability Lab is a public SRE and platform engineering portfolio project that models a production-readiness observability stack on a local workstation. It runs real FastAPI services, emits metrics/logs/traces, provisions Grafana dashboards and alerting rules, validates Kubernetes manifests, and enforces CI quality gates for Python, containers, infrastructure, and dependency security.

The project is intentionally local-first. It is built to demonstrate engineering judgment around service instrumentation, incident workflows, CI/CD quality control, and baseline security hardening without pretending that a Docker Compose lab is a fully managed production platform.

## Why This Project Exists

OpsSight exists to show the operational work behind a credible platform engineering portfolio project: designing service telemetry, validating runtime dependencies, failing builds for the right reasons, and documenting how an operator would investigate real failure modes. The goal is not to present a toy dashboard stack; it is to demonstrate how an SRE thinks about evidence, readiness, failure isolation, and safe publication.

## Production-Readiness Goals

- Keep local startup reproducible through Docker Compose.
- Ensure CI validates static quality, tests, infrastructure manifests, containers, security scans, and a full smoke path.
- Preserve deterministic AI RCA behavior when no LLM provider is available.
- Make telemetry useful for incident response, not just chart screenshots.
- Keep production claims realistic: Compose is a lab runtime, while Kubernetes manifests and Helm scaffolding are migration/readiness artifacts.

## What This Project Demonstrates

- FastAPI service design with health checks, standardized responses, request correlation, structured logging, and Prometheus metrics.
- Dependency simulation through a separate payment-gateway service with latency and failure controls.
- OpenTelemetry traces exported through Grafana Alloy and stored in Tempo.
- Loki log ingestion with trace/correlation IDs for incident investigation.
- Prometheus recording rules, burn-rate alerts, service health signals, and SLO-oriented dashboards.
- Grafana dashboards for SRE overview, API golden signals, incident investigation, Docker runtime, Kubernetes operations, workstation telemetry, and AI runtime monitoring.
- Local-first AI RCA workflows with deterministic `rule_based` fallback and optional Ollama/LM Studio/OpenAI-compatible providers.
- Docker Compose runtime with non-root custom service containers and local-demo security boundaries.
- Kubernetes and Helm-ready manifests for migration/readiness review.
- Split GitHub Actions quality gates: Ruff, mypy, pytest, YAML validation, Docker build, KIND-backed Kubernetes validation, smoke testing, pip-audit, and Trivy.
- CodeQL Python static analysis as a separate code-scanning workflow.
- Public repository governance through Dependabot, CODEOWNERS, issue/PR templates, SECURITY.md, CONTRIBUTING.md, secret scanning, push protection, and branch protection.

## Architecture Overview

```mermaid
flowchart TB
  Dev[Developer / CI Runner] --> Compose[Docker Compose Runtime]
  Dev --> GHA[GitHub Actions CI/CD]
  GHA --> Quality[Lint, Format, Type Check, Unit Tests]
  GHA --> Infra[Compose, YAML, KIND + kubectl Dry Run]
  GHA --> Sec[pip-audit + Trivy]
  GHA --> Build[Docker Build + Smoke Test Stack]

  Compose --> API[FastAPI Orders API]
  Compose --> Pay[Payment Gateway Dependency]
  Compose --> RCA[AI RCA Service]
  Compose --> Exporter[Local Runtime Exporter]

  API --> Pay
  API --> Metrics[/metrics]
  Pay --> Metrics
  RCA --> Metrics
  Exporter --> Metrics

  API --> Logs[JSON stdout logs]
  Pay --> Logs
  RCA --> Logs

  API --> Traces[OTLP traces]
  Pay --> Traces
  RCA --> Traces

  Metrics --> Alloy[Grafana Alloy]
  Logs --> Alloy
  Traces --> Alloy

  Alloy --> Prom[Prometheus]
  Alloy --> Loki[Loki]
  Alloy --> Tempo[Tempo]

  Prom --> Grafana[Grafana Dashboards and Alerts]
  Loki --> Grafana
  Tempo --> Grafana

  K8s[Kubernetes Manifests] --> Infra
```

## Core Services

| Service | Path | Port | Purpose |
| --- | --- | ---: | --- |
| Orders API | `apps/api` | `8000` | User-facing FastAPI service with order endpoints, middleware, metrics, traces, and failure simulations. |
| Payment gateway | `apps/dependency` | `8081` | Observable downstream dependency used to model latency, 503s, and dependency degradation. |
| AI RCA | `apps/ai-rca` | `8090` | Incident analysis API for alert explanation, log/trace summaries, RCA hypotheses, and persisted RCA artifacts. |
| Local runtime exporter | `apps/local-runtime-exporter` | `9108` | Workstation runtime telemetry exporter for Docker, Ollama, WSL/Linux host metrics, and optional GPU signals. |

## Observability Stack

| Component | Path | Role |
| --- | --- | --- |
| Prometheus | `observability/prometheus` | Metrics scraping, recording rules, burn-rate calculations, and alert rules. |
| Grafana | `observability/grafana` | Provisioned dashboards, alerting resources, and incident investigation views. |
| Loki | `observability/loki` | Log storage for structured application and runtime logs. |
| Tempo | `observability/tempo` | Trace storage for OpenTelemetry spans. |
| Grafana Alloy | `observability/alloy` | Local collector for metrics, logs, and OTLP traces. |
| k6 | `load/k6` | Smoke, spike, and sustained load profiles. |

For a deeper telemetry-flow breakdown, see [docs/observability-architecture.md](docs/observability-architecture.md).

## CI/CD Quality Gates

The workflow in `.github/workflows/ci.yml` is split into explicit jobs so failures identify the broken layer quickly.

| Gate | What it validates | Risk reduced |
| --- | --- | --- |
| Lint and format | `ruff check` and `ruff format --check` over `apps`, `scripts`, and `tests`. | Style drift, import disorder, unused code, and CI failures from formatting differences. |
| Type check | `mypy --no-incremental` for API, dependency, and AI RCA service packages. | Interface drift, incorrect typing assumptions, and stale mypy cache behavior. |
| Unit tests | Service-scoped pytest for API and AI RCA plus repository-level postmortem tests. | Behavioral regressions and Python package import collisions between service-local `app` packages. |
| Validate infra | YAML linting, Docker Compose config validation, KIND cluster startup, and `kubectl apply --dry-run=client --validate=false`. | Invalid manifests, broken Compose syntax, and Kubernetes readiness regressions. |
| Security scan | `pip-audit` over all Python requirement files and Trivy filesystem scan. | Known vulnerable dependencies and high-severity filesystem findings. |
| CodeQL | Python static analysis in a separate CodeQL workflow. | Code-level security and correctness findings surfaced through GitHub code scanning. |
| Build containers | `docker compose build`. | Dockerfile, dependency, and build-context failures. |
| Smoke test stack | `docker compose up -d --build` followed by `scripts/smoke-test.sh`. | Runtime wiring failures across API, dependency, metrics, Prometheus, Loki, Tempo, Grafana, and sample API endpoints. |

The smoke test validates:

- API OpenAPI readiness
- dependency service readiness
- API and dependency metrics endpoints
- Prometheus health and query API
- Loki readiness
- Tempo readiness
- Grafana readiness
- sample `/api/v1/orders` endpoint availability

## Security and Governance

Current baseline controls:

- `pip-audit` dependency scanning in CI.
- Trivy filesystem scanning in CI.
- CodeQL Python static analysis in `.github/workflows/codeql.yml`.
- Dependabot version-update configuration for GitHub Actions and Python requirements.
- GitHub secret scanning enabled.
- GitHub push protection enabled.
- Branch protection on `main` requiring the split CI checks.
- Required pull request review count of one on `main`.
- CODEOWNERS, issue templates, PR template, SECURITY.md, and CONTRIBUTING.md.
- Custom application containers run as non-root users.
- Local app services use read-only root filesystems, dropped Linux capabilities, no-new-privileges, and tmpfs-backed `/tmp` where compatible.
- API-facing FastAPI services set conservative security headers.
- Grafana `admin` / `admin` credentials are documented as local-demo only and can be overridden through environment variables.

Dependabot security updates are not currently enabled in repository settings; Dependabot is configured for version-update governance. Docker socket and host filesystem mounts are local observability features and should not be used as-is in production.

## Operational Scenarios

The lab is designed around realistic failure modes:

- Dependency outage: payment-gateway errors increase API failures and trigger dependency-focused investigation.
- Observability degradation: Prometheus, Loki, Tempo, or Grafana readiness failures block smoke validation even if app containers start.
- Startup sequencing failure: API readiness depends on downstream and telemetry startup behavior instead of assuming all containers are ready immediately.
- Metrics validation failure: smoke testing requires expected metric families to exist, catching instrumentation regressions.
- RCA workflow degradation: AI RCA must continue with deterministic `rule_based` output when an external LLM provider is unavailable.

## Failure Simulation Philosophy

Failure scenarios should be reproducible, observable, and reversible. A scenario is useful only when it produces evidence in at least two telemetry planes, such as metrics plus logs or logs plus traces. Smoke checks should not be weakened to make a demo pass; runtime failures should be fixed at the service, dependency, or telemetry pipeline boundary.

## Local Development Quickstart

Prerequisites:

- Docker Desktop with Compose
- Bash-compatible shell for scripts
- Python 3.12 for local quality checks
- Optional: `make`, `kubectl`, and `jq`

Clone and start:

```bash
git clone https://github.com/capujm10/OpsSight-Observability-Lab.git
cd OpsSight-Observability-Lab

docker compose build
docker compose up -d
bash scripts/smoke-test.sh
```

Stop and clean local volumes:

```bash
docker compose down -v --remove-orphans
```

Python quality checks:

```bash
python -m ruff check apps scripts tests
python -m ruff format --check apps scripts tests
python -m pytest tests
```

Service-scoped tests:

```bash
cd apps/api
python -m pytest

cd ../ai-rca
python -m pytest
```

The services intentionally use service-local packages named `app`; run service tests from each service directory to avoid mixed import contexts.

## Docker Compose Usage

Start the full stack:

```bash
docker compose up -d --build
```

Useful endpoints:

| Component | URL |
| --- | --- |
| API docs | `http://localhost:8000/docs` |
| Payment gateway readiness | `http://localhost:8081/health/ready` |
| AI RCA readiness | `http://localhost:8090/health/ready` |
| Grafana | `http://localhost:3000` |
| Prometheus | `http://localhost:9090` |
| Loki | `http://localhost:3100` |
| Tempo | `http://localhost:3200` |
| Alloy | `http://localhost:12345` |

Local Grafana default:

```text
username: admin
password: admin
```

Set `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` before exposing Grafana outside a trusted local workstation.

## Smoke Testing

Run:

```bash
bash scripts/smoke-test.sh
```

Override endpoints if needed:

```bash
BASE_URL=http://localhost:8000 \
DEPENDENCY_URL=http://localhost:8081 \
GRAFANA_URL=http://localhost:3000 \
PROM_URL=http://localhost:9090 \
LOKI_URL=http://localhost:3100 \
TEMPO_URL=http://localhost:3200 \
bash scripts/smoke-test.sh
```

## Kubernetes Validation

Kubernetes manifests live under:

- `k8s/base`
- `k8s/api`
- `k8s/monitoring`
- `k8s/overlays/local`

CI starts a KIND cluster and validates manifests with:

```bash
kubectl apply --dry-run=client --validate=false -f k8s/base -f k8s/api -f k8s/monitoring
```

Local validation example:

```bash
kubectl apply --dry-run=client --validate=false -f k8s/base -f k8s/api -f k8s/monitoring
```

Full deployment requires a Kubernetes cluster, image publishing strategy, ingress/TLS configuration, storage classes, and real secret management.

## Repository Structure

```text
apps/
  api/                     FastAPI orders service
  dependency/              Observable payment-gateway dependency
  ai-rca/                  AI-assisted RCA service with deterministic fallback
  local-runtime-exporter/  Docker/Ollama/host runtime metrics exporter
observability/
  alloy/                   Grafana Alloy collector config
  prometheus/              Prometheus scrape config, rules, and file SD
  grafana/                 Dashboards, datasources, and alerting provisioning
  loki/                    Loki config
  tempo/                   Tempo config
k8s/                       Kubernetes readiness manifests
helm/                      Helm packaging scaffold
load/k6/                   k6 load profiles
scripts/                   Smoke, simulation, RCA, and postmortem utilities
docs/                      Architecture, runbooks, security, AI RCA, and audit docs
incident-postmortems/      Templates, examples, and generated postmortems
.github/                   CI, Dependabot, ownership, and collaboration templates
```

## Screenshots

Screenshot placeholders are tracked under `docs/screenshots/`.

Recommended public portfolio screenshots:

- Grafana dashboards: SRE Overview, API Golden Signals, Incident Investigation, AI Runtime Monitoring.
- Prometheus: targets page and active alert/rule views.
- Tempo: dependency trace from an API request.
- Loki: structured logs filtered by `correlation_id` or `trace_id`.
- GitHub Actions: CI workflow showing split quality gates and CodeQL workflow.

No screenshot files are invented in this repository. Capture real images after `docker compose up -d --build`, load generation, and at least one incident scenario.

## Roadmap

- Add real dashboard screenshots after a full local run.
- Add SBOM generation and signed image provenance for release builds.
- Add production Helm values for external secrets, persistent storage, ingress TLS, and managed telemetry backends.
- Add authentication/authorization controls before exposing API or AI RCA endpoints beyond localhost.
- Add Grafana annotations from generated RCA milestones.
- Add release workflow for tagged container builds.
- Add dashboard screenshot regression checks after Grafana upgrades.

## Release Process

Releases follow semantic versioning and are recorded in [CHANGELOG.md](CHANGELOG.md).

1. Run local quality gates and smoke validation.
2. Confirm GitHub Actions CI and CodeQL pass on the release branch.
3. Update `CHANGELOG.md` with the release date, notable changes, security notes, and validation evidence.
4. Tag the release as `vMAJOR.MINOR.PATCH`.
5. Publish release notes that distinguish local-lab readiness from production deployment requirements.

## Interview Talking Points

- How the API propagates correlation IDs and trace IDs across logs, metrics, and traces.
- Why CI runs service tests in service directories instead of one mixed Python import context.
- How SLO burn-rate rules connect metrics to actionable incident response.
- Why Docker socket and host mounts are acceptable for a local observability lab but not production.
- How deterministic AI RCA fallback keeps incident analysis usable without an LLM provider.
- How split CI gates improve diagnosis compared with one long validation job.
- What would change when migrating from Compose to Kubernetes or managed telemetry backends.

## License and Contribution Notes

This repository is licensed under the [MIT License](LICENSE).

See [CONTRIBUTING.md](CONTRIBUTING.md) for local development and pull request expectations. Report suspected vulnerabilities through the process in [SECURITY.md](SECURITY.md).
