# Troubleshooting

Use Docker Compose for the full local observability stack. Kustomize validation checks Kubernetes application and monitoring manifests, but it does not start the local Prometheus/Grafana/Loki/Tempo runtime.

Check service state:

```bash
docker compose ps
docker compose logs -f api alloy prometheus loki tempo grafana
```

Verify API telemetry:

```bash
curl http://localhost:8000/health/ready
curl http://localhost:8000/metrics
curl "http://localhost:9090/api/v1/query?query=opsight_http_requests_total"
```

If metrics are missing, inspect Alloy at `http://localhost:12345` and confirm the `prometheus.scrape.api` component is healthy.

If logs are missing, confirm the Docker socket is mounted into Alloy and query:

```logql
{service="opsight-api"} | json
```

If traces are missing, confirm the API environment variable `OPSIGHT_OTEL_EXPORTER_OTLP_ENDPOINT=http://alloy:4317` and query Tempo from Grafana Explore.

Validate Kustomize overlays when Kubernetes manifests fail CI:

```bash
bash scripts/validate-kustomize.sh
kubectl kustomize k8s/overlays/local
```
