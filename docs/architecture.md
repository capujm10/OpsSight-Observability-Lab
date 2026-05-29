# Architecture

OpsSight Observability Lab is a local cloud-native observability ecosystem for a production-style FastAPI service.

```mermaid
flowchart LR
  Client[Client, k6, or incident script] --> API[FastAPI Orders API]
  API --> Payment[Payment Gateway]
  Alert[Alertmanager-compatible payloads] --> RCA[AI RCA Service]
  Exporter[Local Runtime Exporter] -->|Prometheus metrics endpoint| Alloy
  API -->|Prometheus metrics endpoint| Alloy[Grafana Alloy]
  Payment -->|Prometheus metrics endpoint| Alloy
  RCA -->|Prometheus metrics endpoint| Alloy
  API -->|OTLP traces| Alloy
  Payment -->|OTLP traces| Alloy
  RCA -->|OTLP traces| Alloy
  API -->|JSON stdout logs| Docker[Docker logging]
  Payment -->|JSON stdout logs| Docker
  RCA -->|JSON stdout logs| Docker
  Docker --> Alloy
  Alloy -->|remote_write| Prometheus
  Alloy -->|push logs| Loki
  Alloy -->|OTLP traces| Tempo
  Prometheus --> Grafana
  Loki --> Grafana
  Tempo --> Grafana
```

The platform intentionally separates telemetry production from telemetry routing. The API and payment dependency emit structured logs, Prometheus metrics, and OTLP traces. Alloy acts as the local collector and routes each signal to the correct backend.

Ports:

- API: `http://localhost:8000`
- Payment gateway: `http://localhost:8081`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Loki: `http://localhost:3100`
- Tempo: `http://localhost:3200`
- Alloy: `http://localhost:12345`
