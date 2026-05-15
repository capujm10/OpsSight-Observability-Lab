from app.models.rca import IncidentContext, RCAHypothesis, RCAResponse
from app.providers.base import AIProvider, ProviderResult


class RuleBasedProvider(AIProvider):
    name = "rule_based"

    def __init__(self, model: str = "deterministic-heuristics") -> None:
        self.model = model

    async def generate_rca(self, context: IncidentContext, prompt: str) -> ProviderResult:
        service = _primary_service(context)
        dependency = context.dependency or _detect_dependency(context)
        incident_domain = _incident_domain(context)
        latency = context.p95_latency_seconds or 0
        burn = context.burn_rate or 0
        error_rate = context.error_rate or 0
        impacted_slos = context.impacted_slos or _infer_slos(burn, error_rate, latency)

        summary = _summary(context, service, dependency, burn, latency, error_rate, incident_domain)
        causes = _hypotheses(context, service, dependency, burn, latency, error_rate, incident_domain)
        actions = _actions(context, dependency, burn, latency, error_rate, incident_domain)
        logs = _log_analysis(context)
        traces = _trace_analysis(context, dependency)

        response = RCAResponse(
            summary=summary,
            alert_explanation=_alert_explanation(context, impacted_slos, burn, error_rate, latency),
            trace_analysis=traces,
            log_analysis=logs,
            likely_root_causes=causes,
            impacted_slos=impacted_slos,
            recommended_actions=actions,
            risk_notes=[
                "AI output is an investigation aid; validate against Prometheus, Loki, Tempo, and deployment history.",
                "Do not close the incident until recovery is visible in SLO windows and customer-facing checks.",
            ],
            telemetry_references={
                "grafana_links": context.grafana_links,
                "loki_queries": context.logs.loki_queries,
                "tempo_traces": [f"trace_id={trace_id}" for trace_id in context.traces.trace_ids],
                "correlation_ids": context.logs.correlation_ids,
            },
            provider=self.name,
            model=self.model,
            fallback_used=False,
            confidence="high" if causes and causes[0].confidence == "high" else "medium",
        )
        estimated_tokens = max(1, round(len(prompt) / 4))
        return ProviderResult(response=response, prompt_tokens=estimated_tokens, completion_tokens=350)


def _primary_service(context: IncidentContext) -> str:
    if context.alert:
        return context.alert.service
    return context.affected_services[0] if context.affected_services else "unknown-service"


def _detect_dependency(context: IncidentContext) -> str | None:
    for value in context.affected_services + context.traces.services + context.logs.patterns:
        if "payment" in value or "gateway" in value:
            return "payment-gateway"
        if "ollama" in value.lower():
            return "ollama"
        if "docker" in value.lower():
            return "docker-desktop"
        if "kubernetes" in value.lower() or "kube" in value.lower():
            return "local-kubernetes"
    return None


def _incident_domain(context: IncidentContext) -> str:
    values: list[str] = []
    if context.alert:
        values.extend([context.alert.name, context.alert.service, *context.alert.labels.values()])
    values.extend(context.affected_services)
    values.extend(context.logs.patterns)
    joined = " ".join(values).lower()
    if any(token in joined for token in ["ollama", "gpu", "vram", "inference", "ai-runtime"]):
        return "ai-runtime"
    if any(token in joined for token in ["docker", "container", "cadvisor"]):
        return "docker"
    if any(token in joined for token in ["kubernetes", "kube", "pod", "crashloop", "namespace"]):
        return "kubernetes"
    if any(token in joined for token in ["windows", "wsl", "workstation", "disk", "cpu", "service"]):
        return "workstation"
    return "application"


def _infer_slos(burn: float, error_rate: float, latency: float) -> list[str]:
    slos: list[str] = []
    if burn > 1 or error_rate > 0:
        slos.append("availability-99.9")
    if latency > 1:
        slos.append("api-p95-latency")
    return slos or ["no-confirmed-slo-impact"]


def _summary(
    context: IncidentContext, service: str, dependency: str | None, burn: float, latency: float, error_rate: float, domain: str
) -> str:
    if domain == "ai-runtime":
        return (
            f"{service} experienced local AI runtime degradation. The leading hypothesis is Ollama inference latency or failures "
            "caused by model load pressure, GPU VRAM exhaustion, CPU fallback, or memory contention; validate with Ollama, GPU, "
            "WSL2, and container metrics before declaring recovery."
        )
    if domain == "docker":
        return (
            f"{service} experienced Docker runtime instability. Container health, restart count, cAdvisor CPU/memory, filesystem, "
            "and network signals should be correlated to isolate whether the trigger was crash loop, resource pressure, or disk growth."
        )
    if domain == "kubernetes":
        return (
            f"{service} experienced local Kubernetes instability. Pod restarts, CrashLoopBackOff, node pressure, namespace saturation, "
            "and API server health are the primary signals for root-cause validation."
        )
    if domain == "workstation":
        return (
            f"{service} experienced workstation infrastructure degradation. Windows host, WSL2, Docker Desktop, disk, service, "
            "and event-log telemetry should be treated as first-class incident evidence."
        )
    dependency_clause = (
        f" originated from {dependency} dependency degradation" if dependency else " requires correlation across metrics, logs, and traces"
    )
    impact = []
    if latency:
        impact.append(f"p95 latency around {latency:.2f}s")
    if burn:
        impact.append(f"SLO burn rate near {burn:.1f}x")
    if error_rate:
        impact.append(f"error rate near {error_rate:.2%}")
    signal = " and ".join(impact) if impact else "operational signal degradation"
    return f"{service} experienced {signal}{dependency_clause}, impacting request reliability and incident response posture."


def _alert_explanation(context: IncidentContext, slos: list[str], burn: float, error_rate: float, latency: float) -> str:
    if not context.alert:
        return "No alert payload was supplied; analysis is based on incident telemetry context."
    drivers = []
    if burn:
        drivers.append(f"burn-rate signal {burn:.1f}x")
    if error_rate:
        drivers.append(f"error ratio {error_rate:.2%}")
    if latency:
        drivers.append(f"p95 latency {latency:.2f}s")
    return (
        f"{context.alert.name} fired for {context.alert.service} at {context.alert.severity} severity because "
        f"{', '.join(drivers) if drivers else 'the configured alert expression crossed threshold'}. "
        f"Impacted SLOs: {', '.join(slos)}."
    )


def _trace_analysis(context: IncidentContext, dependency: str | None) -> str:
    fragments = []
    if context.traces.slow_spans:
        fragments.append(f"Slow spans: {', '.join(context.traces.slow_spans)}.")
    if context.traces.failed_spans:
        fragments.append(f"Failed spans: {', '.join(context.traces.failed_spans)}.")
    if dependency:
        fragments.append(f"Dependency timing should be inspected around {dependency} spans for propagation into upstream API latency.")
    if context.traces.trace_ids:
        fragments.append(f"Primary Tempo traces: {', '.join(context.traces.trace_ids)}.")
    return " ".join(fragments) or "No trace IDs were supplied; capture Tempo traces before final RCA."


def _log_analysis(context: IncidentContext) -> str:
    fragments = []
    if context.logs.patterns:
        fragments.append(f"Repeated log patterns: {', '.join(context.logs.patterns)}.")
    if context.logs.exception_signatures:
        fragments.append(f"Exception signatures: {', '.join(context.logs.exception_signatures)}.")
    if context.logs.correlation_ids:
        fragments.append(f"Correlation IDs for pivoting: {', '.join(context.logs.correlation_ids)}.")
    return " ".join(fragments) or "No Loki patterns were supplied; query ERROR logs by service and status_code before final RCA."


def _hypotheses(
    context: IncidentContext, service: str, dependency: str | None, burn: float, latency: float, error_rate: float, domain: str
) -> list[RCAHypothesis]:
    causes: list[RCAHypothesis] = []
    if domain == "ai-runtime":
        causes.append(
            RCAHypothesis(
                cause=(
                    "Ollama inference latency increased due to GPU VRAM pressure, "
                    "model load churn, CPU fallback, or local memory contention"
                ),
                confidence="high" if "gpu" in " ".join(context.logs.patterns).lower() or latency > 10 else "medium",
                supporting_signals=context.logs.patterns
                + [signal.name for signal in context.metrics]
                + [f"p95_latency_seconds={latency:.2f}"],
                impacted_systems=[service, "ollama", "gpu", "wsl2"],
                validation_steps=[
                    "Open the OpsSight AI Runtime Monitoring dashboard and compare Ollama p95 latency with VRAM pressure.",
                    "Check opsight_gpu_memory_bytes, opsight_gpu_utilization_percent, and opsight_ollama_tokens_per_second.",
                    "Validate whether WSL2 load or memory pressure rose before the inference latency spike.",
                ],
            )
        )
    if domain == "docker":
        causes.append(
            RCAHypothesis(
                cause=(
                    "Local Docker runtime instability from unhealthy containers, restart loops, resource saturation, or filesystem growth"
                ),
                confidence="high" if context.alert and "Restart" in context.alert.name else "medium",
                supporting_signals=context.logs.patterns + [signal.name for signal in context.metrics],
                impacted_systems=[service, "docker-desktop"],
                validation_steps=[
                    "Open the OpsSight Docker Runtime dashboard and identify containers with restart or unhealthy signals.",
                    "Correlate cAdvisor CPU, memory, filesystem, and network metrics around the alert timestamp.",
                    "Inspect container logs in Loki and docker compose ps for the exit reason.",
                ],
            )
        )
    if domain == "kubernetes":
        causes.append(
            RCAHypothesis(
                cause="Local Kubernetes workload degradation from CrashLoopBackOff, pod restarts, node pressure, or namespace saturation",
                confidence="high" if context.alert and "CrashLoop" in context.alert.name else "medium",
                supporting_signals=context.logs.patterns + [signal.name for signal in context.metrics],
                impacted_systems=[service, "local-kubernetes"],
                validation_steps=[
                    "Open the OpsSight Kubernetes Operations dashboard and inspect pod restart and CrashLoopBackOff panels.",
                    "Run kubectl describe pod for the affected namespace and check recent events.",
                    "Compare node pressure conditions with pod resource requests and limits.",
                ],
            )
        )
    if domain == "workstation":
        causes.append(
            RCAHypothesis(
                cause=(
                    "Workstation infrastructure pressure from Windows CPU, disk, service failure, WSL2 memory pressure, or event-log errors"
                ),
                confidence="medium",
                supporting_signals=context.logs.patterns + [signal.name for signal in context.metrics],
                impacted_systems=[service, "windows-host", "wsl2", "docker-desktop"],
                validation_steps=[
                    "Open the OpsSight Workstation Operations dashboard and check CPU, disk, service, network, and WSL2 panels.",
                    "Review Loki Windows Event Log entries around the incident start time.",
                    "Confirm Docker Desktop and WSL2 service health before restarting application workloads.",
                ],
            )
        )
    if dependency:
        causes.append(
            RCAHypothesis(
                cause=f"{dependency} latency or failure degradation",
                confidence="high" if error_rate > 0 or latency > 1 else "medium",
                supporting_signals=context.logs.patterns + context.traces.slow_spans + [f"burn_rate={burn:.1f}x"],
                impacted_systems=[service, dependency],
                validation_steps=[
                    f"Open Tempo traces and inspect spans crossing from {service} to {dependency}.",
                    "Compare dependency p95 latency against API p95 latency in Grafana.",
                    "Filter Loki logs by correlation_id and dependency error patterns.",
                ],
            )
        )
    if burn > 14:
        causes.append(
            RCAHypothesis(
                cause="Availability SLO fast burn from concentrated 5xx responses",
                confidence="high",
                supporting_signals=[f"burn_rate={burn:.1f}x", f"error_rate={error_rate:.2%}"],
                impacted_systems=[service],
                validation_steps=[
                    "Check burn-rate panels over 5m and 1h windows.",
                    "Confirm top failing endpoints and status code distribution.",
                ],
            )
        )
    if latency > 1:
        causes.append(
            RCAHypothesis(
                cause="Request latency regression from slow downstream path or saturation",
                confidence="medium",
                supporting_signals=[f"p95_latency_seconds={latency:.2f}", *context.traces.slow_spans],
                impacted_systems=context.affected_services or [service],
                validation_steps=[
                    "Inspect slowest endpoint panel.",
                    "Verify whether active requests or dependency latency increased first.",
                ],
            )
        )
    return causes or [
        RCAHypothesis(
            cause="Insufficient telemetry to isolate a single root cause",
            confidence="low",
            supporting_signals=["No dominant dependency, latency, or error signal supplied."],
            impacted_systems=context.affected_services or [service],
            validation_steps=["Collect Prometheus alert payload, Loki error samples, and Tempo traces before publishing RCA."],
        )
    ]


def _actions(context: IncidentContext, dependency: str | None, burn: float, latency: float, error_rate: float, domain: str) -> list[str]:
    actions = ["Declare or maintain incident ownership until SLO recovery is visible."]
    if domain == "ai-runtime":
        actions.extend(
            [
                "Reduce concurrent inference load or unload unused Ollama models.",
                "If VRAM is saturated, switch to a smaller model or lower context size before retrying the workload.",
                "Verify whether CPU fallback is active by comparing GPU utilization, WSL2 load, and token throughput.",
            ]
        )
    if domain == "docker":
        actions.extend(
            [
                "Stop non-critical local containers and validate memory/filesystem recovery.",
                "Restart only the unhealthy container after collecting logs and exit state.",
            ]
        )
    if domain == "kubernetes":
        actions.extend(
            [
                "Scale down or roll back the unstable workload after capturing pod events and previous logs.",
                "Validate node pressure and namespace resource requests before reintroducing load.",
            ]
        )
    if domain == "workstation":
        actions.extend(
            [
                "Preserve Windows Event Log and service state evidence before restarting Docker Desktop, WSL2, or host services.",
                "Free disk or memory pressure first when host saturation is visible.",
            ]
        )
    if dependency:
        actions.append(f"Inspect {dependency} health, saturation, and recent changes; apply fallback or traffic reduction if degraded.")
    if burn > 14 or error_rate > 0.05:
        actions.append("Stop the failing traffic pattern or rollback the release causing elevated 5xx responses.")
    if latency > 1:
        actions.append(
            "Reduce latency pressure by disabling expensive paths, throttling non-critical traffic, or scaling the saturated service."
        )
    actions.extend(
        [
            "Validate readiness probes and customer-facing synthetic checks.",
            "Update the postmortem with verified telemetry before closure.",
        ]
    )
    return actions
