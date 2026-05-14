# Operational Runbook

Start platform:

```bash
docker compose up -d --build
```

Generate normal traffic:

```bash
bash scripts/generate-load.sh
```

Trigger incidents:

```bash
bash scripts/simulate-latency.sh
bash scripts/simulate-errors.sh
curl http://localhost:8000/api/v1/simulate/dependency-failure
```

Run realistic traffic:

```bash
docker compose --profile load run --rm k6 run /scripts/smoke.js
docker compose --profile load run --rm k6 run /scripts/spike.js
docker compose --profile load run --rm k6 run /scripts/sustained.js
```

Validate recovery:

```bash
bash scripts/smoke-test.sh
curl http://localhost:9090/api/v1/alerts
```

Default Grafana credentials:

- User: `admin`
- Password: `admin`

SLO triage:

1. Open `OpsSight SRE Overview`.
2. Check availability SLI, error budget remaining, and burn-rate panels.
3. If burn rate is high, open top failing endpoints and current incident logs.
4. Pivot from Loki trace ID into Tempo.
5. Confirm whether failure originates in API code or the payment-gateway dependency.
