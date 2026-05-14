# OpsSight Demo Walkthrough

This walkthrough frames OpsSight as an internal SaaS observability and incident operations platform.

## 1. Startup

```bash
docker compose up -d --build
docker compose ps
```

Open:

- Grafana: <http://localhost:3000>
- API: <http://localhost:8000/health/ready>
- AI RCA: <http://localhost:8090/health/ready>

Default Grafana credentials are `admin` / `admin`.

## 2. Generate Baseline Traffic

```bash
bash scripts/generate-load.sh
```

In Grafana, open the API Golden Signals dashboard and confirm request rate, status distribution, and latency panels are populated.

## 3. Simulate an Incident

Dependency degradation:

```bash
make dependency
```

Latency regression:

```bash
make latency
```

Error burst:

```bash
make errors
```

## 4. Alert and SLO Review

Open Prometheus or Grafana alerting views and inspect:

- `OpsSightDependencyDegradation`
- `OpsSightElevated5xxResponses`
- `OpsSightSLOFastBurn`
- `OpsSightHighP95Latency`

Use the SRE Overview dashboard to review availability SLI, error budget burn, service uptime, dependency health, and AI RCA readiness.

## 5. Investigation Workflow

Follow the operational pivot:

```text
SLO burn or alert
-> Golden Signals panel
-> top failing endpoint
-> Loki logs by service/correlation_id
-> Tempo trace by trace_id
-> dependency span timing
-> RCA hypothesis
-> mitigation
-> recovery validation
```

Relevant Loki pivots:

```logql
{service="opsight-api",severity="ERROR"} | json
{service="payment-gateway"} | json | outcome="failure"
{service=~"opsight-api|payment-gateway"} | json | correlation_id="trace-chain-check"
```

## 6. AI RCA Workflow

Run deterministic RCA without external API keys:

```bash
AI_PROVIDER=rule_based docker compose up -d --build ai-rca
python scripts/sample-ai-rca.py
```

The response includes:

- concise incident summary
- alert explanation
- trace analysis
- log analysis
- ranked hypotheses
- remediation recommendations
- Grafana, Loki, Tempo, and correlation references

Replay an Alertmanager-compatible alert and let AI RCA enrich it with live Prometheus, Loki, and Tempo queries:

```bash
python scripts/send-alertmanager-webhook.py
```

Generated RCA markdown and JSON artifacts are written under `artifacts/ai-rca/`.

## 7. Postmortem Generation

```bash
make postmortems
```

Open the generated markdown under `incident-postmortems/generated/` and review:

- incident timeline
- telemetry references
- Grafana annotations
- AI-Assisted RCA Enrichment
- follow-up tasks

## 8. Remediation Validation

Run:

```bash
bash scripts/smoke-test.sh
```

Then confirm:

- `up{job=~"opsight-api|payment-gateway|opsight-ai-rca"}` is healthy.
- API 5xx rate returns to baseline.
- p95 latency returns below threshold.
- SLO burn rate trends downward.
- Loki no longer shows new dependency failure patterns.
- Tempo traces show successful API-to-dependency spans.

## 9. Interview Storyline

Position the demo around operational maturity:

- OpenTelemetry-first service instrumentation.
- Grafana Alloy as telemetry collection and routing layer.
- Prometheus, Loki, and Tempo correlation.
- SLO and burn-rate incident detection.
- Dependency-aware tracing and log pivots.
- Local-first AI RCA that augments responders.
- Deterministic postmortem generation with telemetry evidence.

## 10. Workstation Monitoring Walkthrough

Start OpsSight and verify the local runtime exporter:

```bash
docker compose up -d --build
curl http://localhost:9108/health/ready
curl http://localhost:9108/metrics
```

Open the OpsSight Workstation Operations dashboard. Confirm:

- `windows-exporter` is up if Windows host monitoring is installed.
- WSL2 memory and load are populated from the local runtime exporter.
- Windows disk, service, network, and Event Log panels populate after host Alloy or windows_exporter setup.

Use [docs/workstation-observability.md](/C:/Users/PERSONAL/Documents/GitHub/OpsSight-Observability-Lab/docs/workstation-observability.md) for the Windows host service setup.

## 11. Docker Incident Walkthrough

Generate a restart-loop scenario:

```powershell
.\scripts\simulate-local-incident.ps1 -Scenario container-crashloop
```

In Grafana:

- Open OpsSight Docker Runtime.
- Confirm restart count and container state changes.
- Check Loki logs for `opsight-crashloop-demo`.
- Review AI RCA output under `artifacts/ai-rca/`.

Expected operational conclusion: a local container restart loop caused Docker runtime instability and should be validated through restart count, exit state, logs, and cAdvisor resource metrics.

## 12. Kubernetes Degradation Walkthrough

Install and expose kube-state-metrics:

```powershell
kubectl create namespace monitoring
kubectl apply -f k8s/monitoring/kube-state-metrics.yaml
kubectl -n monitoring port-forward svc/kube-state-metrics 8080:8080
```

Create a bad pod in any local namespace to trigger CrashLoopBackOff:

```powershell
kubectl run opsight-crashloop --image=alpine:3.20 --restart=Never -- sh -c "exit 42"
```

Open OpsSight Kubernetes Operations and inspect pod restarts, CrashLoopBackOff, node pressure, and namespace health.

## 13. AI Runtime Degradation Walkthrough

Start Ollama locally, then route one request through the OpsSight proxy:

```powershell
$body = @{ model = "llama3.2"; prompt = "Explain local AI runtime observability."; stream = $false } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:9108/ollama/api/generate -ContentType application/json -Body $body
```

Then trigger the RCA workflow:

```powershell
.\scripts\simulate-local-incident.ps1 -Scenario ollama-latency
```

Open OpsSight AI Runtime Monitoring and inspect latency, token throughput, active models, failures, model load time, WSL2 pressure, and GPU panels.

## 14. GPU Saturation Walkthrough

If an NVIDIA GPU and `nvidia-smi` are available, confirm:

```powershell
nvidia-smi
curl http://localhost:9108/metrics
```

Optional DCGM exporter:

```powershell
docker compose --profile gpu up -d dcgm-exporter
```

Trigger the RCA fixture:

```powershell
.\scripts\simulate-local-incident.ps1 -Scenario gpu-saturation
```

Expected RCA framing: Ollama inference latency can increase when GPU VRAM exhaustion forces CPU fallback and reduces token throughput.

## 15. AI RCA Operational Analysis

For workstation incidents, AI RCA now recognizes:

- Windows host pressure and service failures.
- Docker unhealthy containers and restart loops.
- WSL2 memory or CPU pressure.
- Kubernetes CrashLoopBackOff and pod restarts.
- Ollama latency, request failures, model load pressure, token throughput degradation.
- GPU VRAM pressure and CPU fallback risk.

The strongest demo flow is:

```text
Workstation alert
-> domain dashboard
-> local metric and log evidence
-> AI RCA webhook
-> artifact review
-> operational recommendation
-> recovery validation
```
