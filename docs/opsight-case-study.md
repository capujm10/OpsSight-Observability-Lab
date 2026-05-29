# OpsSight Case Study: AI-Native Observability Platform Engineering Lab

## One-Line Positioning

OpsSight is a local-first observability engineering platform that demonstrates how an SRE/platform engineer builds, validates, and governs production-style telemetry workflows without overclaiming production deployment.

## Problem Framing

Many portfolio projects show dashboards but miss operational discipline: reproducible failure scenarios, testable telemetry pipelines, and governance guardrails. OpsSight addresses this gap by combining service instrumentation, incident simulation, structured validation, and AI-assisted RCA workflows.

## Scope and Architecture

Core scope:

- FastAPI services (`api`, `dependency`, `ai-rca`, `local-runtime-exporter`)
- telemetry stack (Prometheus, Loki, Tempo, Grafana, Alloy)
- local runtime via Docker Compose
- Kubernetes manifests and overlays for readiness validation
- operational scripts, runbooks, and postmortem artifacts

The architecture supports metrics, logs, and traces as correlated signals for incident triage, recovery validation, and RCA quality.

## SRE and Platform Engineering Practices Demonstrated

- Golden-signal and SLO-aware monitoring posture.
- Alert simulation and incident scenario reproducibility.
- Deterministic RCA fallback (`rule_based`) when LLM providers are unavailable.
- Split CI quality gates for faster failure isolation (lint/type/test/infra/security/build/smoke).
- Security-aware local setup with explicit production-boundary disclaimers.

## AI-Native Engineering Contribution

OpsSight treats AI as an operational accelerator, not an authority source:

- AI RCA enriches alerts with telemetry context.
- Human operators remain decision owners.
- Markdown + JSON RCA artifact persistence keeps outputs auditable and reusable.
- Rule-based fallback ensures deterministic behavior under provider outages.

## Validation Evidence Model

This repository prioritizes evidence-based engineering:

- local lint/format/test commands,
- Compose and Kubernetes dry-run validation,
- smoke-test and observability-check runtime validation,
- documented incident and postmortem workflows.

The portfolio value comes from proving operational behavior, not claiming scale.

## Results and Recruiter-Relevant Outcomes

What this project signals to hiring teams:

- ability to design and operate telemetry-rich systems,
- fluency in incident response workflows and observability tooling,
- strong quality-gate and governance discipline,
- pragmatic AI integration with deterministic safety fallback,
- clear communication of boundaries, risks, and production-readiness tradeoffs.

## Reuse Guidance

For interviews or portfolio review, position OpsSight as:

- a realistic SRE/platform lab,
- a governed engineering-standards consumer,
- an example of local-first operational maturity,
- and a concrete demonstration of AI-native incident analysis patterns.
