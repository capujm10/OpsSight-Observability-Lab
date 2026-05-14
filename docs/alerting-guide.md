# Alerting Guide

Prometheus alert rules live in `observability/prometheus/rules/alert-rules.yml`. Grafana-managed alert examples are provisioned in `observability/grafana/provisioning/alerting/rules.yml`.

Implemented alert classes:

- API unavailable
- Elevated 5xx responses
- p95 latency above threshold
- Dependency degradation
- Excessive error rate
- Failed readiness checks

Each rule includes severity, probable causes, and remediation guidance. Alert thresholds are intentionally sensitive for a local lab so incidents can be reproduced quickly.
