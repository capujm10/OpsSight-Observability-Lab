# Synthetic Monitoring

OpsSight includes a lightweight synthetic monitor for local runtime validation. It complements `scripts/smoke-test.sh`: smoke testing validates stack readiness, while synthetic monitoring exercises a small user path and verifies telemetry side effects.

## Script

Run:

```bash
bash scripts/synthetic-monitor.sh
```

Or through Make:

```bash
make synthetic-monitor
```

## What It Checks

- API readiness through `/health/ready`.
- Payment-gateway readiness through `/health/ready`.
- API metrics endpoint contains `opsight_http_requests_total`.
- Dependency metrics endpoint contains `opsight_payment_requests_total`.
- A request to `/api/v1/orders` returns a usable `x-trace-id`.
- Prometheus query API can query `up{job="opsight-api"}`.
- Tempo readiness endpoint responds.

## Endpoint Overrides

```bash
BASE_URL=http://localhost:8000 \
DEPENDENCY_URL=http://localhost:8081 \
PROM_URL=http://localhost:9090 \
TEMPO_URL=http://localhost:3200 \
bash scripts/synthetic-monitor.sh
```

## Operating Notes

- Run after `docker compose up -d --build`.
- Use it after incident simulations to verify recovery.
- It does not replace full smoke testing or CI; it is a fast operator check for availability, metrics, and trace generation.
- A missing `x-trace-id` is treated as a failure because it breaks the logs-to-traces investigation workflow.
