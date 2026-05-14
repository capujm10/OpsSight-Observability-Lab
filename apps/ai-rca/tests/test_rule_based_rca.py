import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.models.rca import AlertContext, IncidentContext, LogContext, TelemetrySignal, TraceContext  # noqa: E402
from app.providers.llm import OllamaProvider  # noqa: E402
from app.providers.rule_based import RuleBasedProvider  # noqa: E402


@pytest.mark.anyio
async def test_rule_based_provider_generates_operational_rca() -> None:
    context = IncidentContext(
        incident_id="INC-TEST-001",
        affected_services=["opsight-api", "payment-gateway"],
        impacted_slos=["availability-99.9", "api-p95-latency"],
        burn_rate=120,
        error_rate=0.12,
        p95_latency_seconds=1.8,
        dependency="payment-gateway",
        alert=AlertContext(name="OpsSightSLOFastBurn", severity="critical", service="opsight-api"),
        traces=TraceContext(trace_ids=["27a51aae7664ac0c0708c9af0ec80334"], slow_spans=["payment-gateway authorize"]),
        logs=LogContext(
            correlation_ids=["trace-chain-check"],
            patterns=["dependency_unavailable", "status_code=503"],
            loki_queries=['{service="opsight-api",severity="ERROR"} | json'],
        ),
    )

    result = await RuleBasedProvider().generate_rca(context, "prompt")

    assert "payment-gateway" in result.response.summary
    assert result.response.likely_root_causes[0].confidence == "high"
    assert "availability-99.9" in result.response.impacted_slos
    assert any("Tempo" in step for step in result.response.likely_root_causes[0].validation_steps)
    assert result.response.telemetry_references["tempo_traces"] == ["trace_id=27a51aae7664ac0c0708c9af0ec80334"]


@pytest.mark.anyio
async def test_ollama_provider_falls_back_to_rule_based_when_unavailable() -> None:
    settings = Settings(AI_BASE_URL="http://127.0.0.1:9", AI_TIMEOUT_SECONDS=0.1, AI_MODEL="llama3.2")
    context = IncidentContext(
        affected_services=["opsight-api", "payment-gateway"],
        burn_rate=42,
        error_rate=0.08,
        dependency="payment-gateway",
        alert=AlertContext(name="OpsSightSLOFastBurn", severity="critical", service="opsight-api"),
    )

    result = await OllamaProvider(settings).generate_rca(context, "prompt")

    assert result.fallback_used is True
    assert result.response.fallback_used is True
    assert result.response.provider == "rule_based"
    assert result.response.likely_root_causes


@pytest.mark.anyio
async def test_rule_based_provider_understands_ai_runtime_incidents() -> None:
    context = IncidentContext(
        incident_id="INC-LOCAL-AI-001",
        affected_services=["ollama", "local-runtime-exporter"],
        p95_latency_seconds=28,
        alert=AlertContext(
            name="OpsSightOllamaLatencySpike",
            severity="warning",
            service="ollama",
            labels={"domain": "ai-runtime"},
        ),
        metrics=[
            TelemetrySignal(name="opsight_gpu_memory_bytes", value=0.94, unit="ratio"),
            TelemetrySignal(name="opsight_ollama_tokens_per_second", value=2.1),
        ],
        logs=LogContext(patterns=["gpu vram pressure", "cpu fallback suspected"]),
    )

    result = await RuleBasedProvider().generate_rca(context, "prompt")

    assert "local AI runtime degradation" in result.response.summary
    assert "Ollama inference latency increased" in result.response.likely_root_causes[0].cause
    assert "gpu" in result.response.likely_root_causes[0].impacted_systems
    assert any("VRAM" in action for action in result.response.recommended_actions)


@pytest.mark.anyio
async def test_rule_based_provider_understands_kubernetes_incidents() -> None:
    context = IncidentContext(
        incident_id="INC-K8S-001",
        affected_services=["local-kubernetes"],
        alert=AlertContext(
            name="OpsSightKubernetesCrashLoopBackOff",
            severity="critical",
            service="kubernetes",
            labels={"domain": "kubernetes"},
        ),
        logs=LogContext(patterns=["CrashLoopBackOff", "pod restart"]),
    )

    result = await RuleBasedProvider().generate_rca(context, "prompt")

    assert "local Kubernetes instability" in result.response.summary
    assert "CrashLoopBackOff" in result.response.likely_root_causes[0].cause
    assert any("kubectl describe pod" in step for step in result.response.likely_root_causes[0].validation_steps)
