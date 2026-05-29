# Observability Context

## Telemetry Concepts

OpsSight uses a three-signal model and expects each core service to provide:

- metrics for service health and SLO behavior,
- structured logs for event-level evidence,
- traces for dependency-path timing and causality.

Correlation IDs and trace IDs are treated as first-class investigation keys across telemetry surfaces.

## Monitoring Philosophy

Monitoring in this repository is operational, not decorative:

- health and readiness checks gate confidence,
- alerts should map to user-impacting conditions,
- dashboards should accelerate diagnosis, not replace it,
- smoke and synthetic checks should fail when telemetry is missing or broken.

The default posture is local-first realism: detect failures early, investigate with linked signals, and validate recovery with concrete evidence.

## Observability Architecture

The architecture follows an instrument -> collect -> store -> investigate flow:

1. FastAPI services and exporter emit metrics/logs/traces.
2. Grafana Alloy collects and routes signals.
3. Prometheus, Loki, and Tempo store telemetry by signal type.
4. Grafana dashboards and alerting connect telemetry to incident workflows.
5. AI RCA workflows consume alerts and telemetry context to accelerate triage while preserving deterministic fallback behavior.

## Recruiter-Facing Engineering Value

OpsSight demonstrates practical platform and SRE strengths:

- production-style observability design under local constraints,
- validation discipline across code, infra, and runtime checks,
- incident simulation and postmortem workflows tied to telemetry,
- AI-assisted operations with deterministic, testable fallback behavior,
- governance-aware engineering decisions suitable for real team environments.
