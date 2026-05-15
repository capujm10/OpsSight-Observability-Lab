# OpsSight Observability Lab

## Mission
Production-style observability engineering laboratory focused on:

- SRE practices
- observability engineering
- DevSecOps
- OpenTelemetry
- CI/CD hardening
- incident simulation
- AI-assisted RCA workflows
- production-readiness validation

This repository should simulate realistic enterprise engineering standards, operational maturity, and platform governance.

---

# Architecture Standards

## Core Stack
- FastAPI microservices
- Docker Compose
- Kubernetes manifests + Kustomize
- Grafana
- Prometheus
- Loki
- Tempo
- Grafana Alloy
- OpenTelemetry

## Services
- api
- dependency
- ai-rca
- local-runtime-exporter

## Observability Requirements
All services should expose:
- health endpoints
- Prometheus metrics
- structured JSON logs
- OpenTelemetry traces
- correlation IDs where applicable

---

# Engineering Rules

## Branch Strategy
- Never commit directly to `main`
- Always use feature branches
- Use pull requests for all changes
- Preserve branch protection rules

## Pull Request Expectations
Every non-trivial PR should include:
- summary
- validation evidence
- operational impact
- rollback considerations
- security considerations
- changed files overview

Keep PRs:
- small
- reversible
- reviewable
- production-oriented

---

# Required Validation

Before every PR:

    python -m ruff check apps scripts tests
    python -m ruff format --check apps scripts tests
    python -m pytest tests

    docker compose config --quiet

    kubectl apply --dry-run=client --validate=false \
      -f k8s/base \
      -f k8s/api \
      -f k8s/monitoring

    bash scripts/smoke-test.sh

---

# Security Rules

- Never expose secrets
- Never commit credentials
- Never weaken CI gates
- Never disable CodeQL
- Never bypass branch protection
- Never suppress security findings without justification
- Prefer least-privilege configurations
- Validate dependency upgrades carefully

---

# Kubernetes Rules

- Prefer Kustomize overlays
- Validate manifests before commit
- Keep manifests modular
- Avoid duplicated YAML definitions
- Use readiness/liveness probes when applicable
- Prefer non-root containers where possible

---

# Dependency Governance

- Prefer incremental upgrades
- Validate telemetry compatibility
- Validate OpenTelemetry version alignment
- Validate Grafana stack compatibility
- Never auto-merge major upgrades without review

---

# Incident Simulation Standards

- Preserve smoke-test coverage
- Preserve failure simulation scenarios
- Preserve observability telemetry flows
- Maintain RCA workflows and operational runbooks

---

# Documentation Standards

When behavior changes:

- update README
- update architecture diagrams
- update runbooks
- update operational notes
- update validation instructions

For operational workflows:

- add runbooks
- add postmortems
- document failure scenarios

---

# AI Agent Expectations

AI coding agents should:

- inspect repository structure before coding
- prefer existing repository patterns
- minimize token usage
- avoid unnecessary rewrites
- preserve architecture consistency
- prefer reversible changes
- validate changes before proposing PRs
- maintain production-style engineering discipline