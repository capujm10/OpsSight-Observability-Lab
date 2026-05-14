# Screenshot Checklist

Capture these screens after `docker compose up -d --build` and after generating load plus an incident scenario.

Recommended set:

1. Grafana home showing provisioned OpsSight dashboards.
2. OpsSight API Golden Signals dashboard with request rate, error rate, and latency percentiles.
3. OpsSight Incident Investigation dashboard with logs, traces, and lifecycle annotations.
4. OpsSight SRE Overview dashboard with SLO state, burn rate, dependency health, and AI RCA readiness.
5. Loki Explore view filtered by `correlation_id`.
6. Tempo trace view opened from a Loki `trace_id` derived field.
7. Prometheus alerts view showing SLO burn or dependency degradation alert state.
8. AI RCA sample output from `python scripts/sample-ai-rca.py`.
9. Generated postmortem showing the AI-Assisted RCA Enrichment section.
10. Recovery validation after mitigation, showing burn-rate trend and service health.

Suggested filenames:

- `01-golden-signals.png`
- `02-incident-investigation.png`
- `03-sre-overview-aiops.png`
- `04-loki-trace-correlation.png`
- `05-tempo-dependency-trace.png`
- `06-burn-rate-alerts.png`
- `07-ai-rca-output.png`
- `08-postmortem-enrichment.png`
