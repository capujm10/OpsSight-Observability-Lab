# Incident Scenarios

## 1. API Downtime

Trigger: `docker compose stop api`

Expected metrics: `up{job="opsight-api"}` becomes absent or zero after scrape timeout.

Expected logs: API logs stop; Docker event history shows container stopped.

Expected traces: no new traces.

Expected alerts: `OpsSightApiUnavailable`.

RCA workflow: confirm container state, inspect recent logs, check health endpoint after restart.

Remediation: `docker compose up -d api`.

## 2. High Latency

Trigger: `bash scripts/simulate-latency.sh`

Expected metrics: p95/p99 latency rises, dependency p95 rises.

Expected logs: `latency simulation triggered`.

Expected traces: slow API span with nested payment gateway span.

Expected alerts: `OpsSightHighP95Latency`.

RCA workflow: compare route latency, inspect slow spans, validate dependency timing.

Remediation: stop scenario traffic and confirm latency returns to baseline.

## 3. Increased 500 Errors

Trigger: `bash scripts/simulate-errors.sh`

Expected metrics: 5xx rate and error ratio rise.

Expected logs: `unhandled exception` with stack trace.

Expected traces: request traces with error status.

Expected alerts: `OpsSightElevated5xxResponses` and possibly `OpsSightExcessiveErrorRate`.

RCA workflow: filter logs by `severity="ERROR"`, identify path, pivot by trace ID.

Remediation: disable bad path, rollback release, or patch exception source.

## 4. Dependency Degradation

Trigger: `curl http://localhost:8000/api/v1/simulate/dependency-failure`

Expected metrics: dependency failure counter increments, 503 responses increase.

Expected logs: `dependency failure simulation triggered` and `dependency failure`.

Expected traces: payment gateway span marked as failed.

Expected alerts: `OpsSightDependencyDegradation`.

RCA workflow: inspect dependency operation, confirm only dependency path is affected.

Remediation: retry policy, circuit breaker, failover, or dependency escalation.

## 5. Partial Service Failure

Trigger: generate normal traffic while repeatedly calling dependency failure.

Expected metrics: `/api/v1/orders` and dependency routes degrade while health remains live.

Expected logs: mixed successful orders and dependency failures.

Expected traces: successful read paths alongside failed dependency spans.

Expected alerts: dependency and 5xx alerts without full API unavailable.

RCA workflow: establish that the process is up, then isolate failing operation and dependency.

Remediation: drain affected workflow, protect read-only routes, and restore downstream dependency.
