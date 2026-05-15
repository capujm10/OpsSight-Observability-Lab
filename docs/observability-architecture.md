# Observability Architecture

This document describes how OpsSight moves telemetry from instrumented services into the local observability stack. The design is intentionally local-first, but the signal paths mirror patterns used in production SRE platforms: collect at service boundaries, centralize through a collector, store in fit-for-purpose backends, and investigate incidents through linked dashboards, logs, traces, and alerts.

## Runtime Topology

```mermaid
flowchart LR
  Client[Load scripts, smoke tests, users] --> API[Orders API]
  API --> Payment[Payment Gateway]
  Alert[Alertmanager-compatible payloads] --> RCA[AI RCA Service]
  Exporter[Local Runtime Exporter] --> Metrics[Prometheus Metrics]

  API --> Metrics
  Payment --> Metrics
  RCA --> Metrics

  API --> Logs[Structured JSON Logs]
  Payment --> Logs
  RCA --> Logs

  API --> Traces[OTLP Traces]
  Payment --> Traces
  RCA --> Traces

  Metrics --> Alloy[Grafana Alloy]
  Logs --> Alloy
  Traces --> Alloy

  Alloy --> Prometheus
  Alloy --> Loki
  Alloy --> Tempo

  Prometheus --> Grafana
  Loki --> Grafana
  Tempo --> Grafana
```

## Metrics Flow

```mermaid
sequenceDiagram
  participant Service as FastAPI services
  participant Exporter as Local runtime exporter
  participant Alloy as Grafana Alloy
  participant Prom as Prometheus
  participant Grafana as Grafana

  Service->>Service: Expose /metrics
  Exporter->>Exporter: Collect Docker/Ollama/host metrics
  Alloy->>Service: Scrape application metrics
  Alloy->>Exporter: Scrape runtime metrics
  Alloy->>Prom: Remote write metrics
  Prom->>Prom: Evaluate rules and alerts
  Grafana->>Prom: Query dashboards and alert context
```

Prometheus stores service request counts, duration histograms, dependency metrics, AI RCA provider metrics, runtime exporter signals, and SLO burn-rate recording rules. Grafana dashboards use those series for golden signals, SRE overview, incident investigation, Docker runtime, Kubernetes operations, workstation telemetry, and AI runtime panels.

## Tracing Flow

```mermaid
sequenceDiagram
  participant Client
  participant API as Orders API
  participant Payment as Payment Gateway
  participant Alloy as Grafana Alloy
  participant Tempo
  participant Grafana

  Client->>API: Request with or without x-correlation-id
  API->>API: Create request span and correlation context
  API->>Payment: Downstream call with trace context
  Payment->>Payment: Create dependency span
  API->>Alloy: Export OTLP spans
  Payment->>Alloy: Export OTLP spans
  Alloy->>Tempo: Write trace data
  Grafana->>Tempo: Open trace from dashboard or log-derived trace_id
```

OpenTelemetry instrumentation is configured in the FastAPI services. Trace IDs are also surfaced in structured logs so operators can pivot from logs to Tempo traces during incident review.

## Log Aggregation Flow

```mermaid
flowchart LR
  API[Orders API stdout] --> Docker[Docker Engine logs]
  Payment[Payment Gateway stdout] --> Docker
  RCA[AI RCA stdout] --> Docker
  Docker --> Alloy[Grafana Alloy log pipeline]
  Alloy --> Loki[Loki]
  Loki --> Grafana[Grafana Explore and dashboards]
```

Application logs are structured JSON and include correlation IDs, trace IDs, severity, HTTP method, route/path, status code, and latency fields where available. Loki is the investigation store for recent errors, request completion logs, and dependency failure patterns.

## Service-to-Service Investigation Path

```mermaid
flowchart TB
  Symptom[Smoke test or alert failure] --> Prom[Check Prometheus target and alert state]
  Prom --> Grafana[Open Grafana dashboard]
  Grafana --> Loki[Filter Loki by service, severity, correlation_id]
  Loki --> Tempo[Open related Tempo trace_id]
  Tempo --> Cause[Identify slow dependency or failing span]
  Cause --> RCA[Run AI RCA or postmortem enrichment]
```

The expected SRE workflow is to start with a service-level symptom, validate it through metrics, pivot into logs for precise failure context, inspect traces for dependency timing and status, and then use the AI RCA service or postmortem generator as an investigation aid.

## CI and Runtime Validation Flow

```mermaid
flowchart LR
  PR[Pull Request] --> Lint[Ruff lint and format]
  Lint --> Types[mypy type checks]
  Lint --> Tests[Service-scoped pytest]
  Lint --> Infra[YAML, Compose, KIND kubectl dry-run]
  Lint --> Security[pip-audit, Trivy, CodeQL]
  Types --> Build[Docker Compose build]
  Tests --> Build
  Infra --> Build
  Build --> Smoke[Compose up and smoke-test.sh]
```

The pipeline separates static correctness, infrastructure validation, security scanning, image build, and runtime smoke testing. This keeps failure domains visible and prevents a working unit-test suite from hiding broken containers or invalid Kubernetes manifests.
