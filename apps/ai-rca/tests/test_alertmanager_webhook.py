import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.models.rca import AlertmanagerWebhook  # noqa: E402
from app.services.alertmanager import incident_from_alert  # noqa: E402
from app.workflows.rca_workflow import RCAWorkflow  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "alertmanager-slo-fast-burn.json"


def test_alertmanager_alert_is_normalized_to_incident_context() -> None:
    payload = AlertmanagerWebhook.model_validate_json(FIXTURE.read_text(encoding="utf-8"))

    context = incident_from_alert(payload.alerts[0])

    assert context.incident_id == "slo-fast-burn-demo"
    assert context.alert is not None
    assert context.alert.name == "OpsSightSLOFastBurn"
    assert context.alert.status == "firing"
    assert context.alert.started_at == "2026-05-14T04:11:56Z"
    assert context.alert.fingerprint == "slo-fast-burn-demo"
    assert context.traces.trace_ids == ["27a51aae7664ac0c0708c9af0ec80334"]
    assert context.logs.correlation_ids == ["trace-chain-check"]


@pytest.mark.anyio
async def test_alertmanager_webhook_enriches_with_live_telemetry_and_persists_artifacts() -> None:
    payload = AlertmanagerWebhook.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    output = ROOT / ".tmp-ai-rca-tests"
    if output.exists():
        shutil.rmtree(output)
    settings = Settings(AI_PROVIDER="rule_based", AI_RCA_ARTIFACT_DIR=str(output))
    workflow = RCAWorkflow(settings)

    async def prometheus_query(query: str) -> dict[str, Any]:
        if "burn_rate:5m" in query:
            return _prometheus_value(120)
        if "status_code" in query:
            return _prometheus_value(0.12)
        if "histogram_quantile" in query:
            return _prometheus_value(1.8)
        return _prometheus_value(1)

    async def loki_query_range(query: str, limit: int = 20) -> dict[str, Any]:
        return {
            "status": "success",
            "data": {
                "result": [
                    {
                        "stream": {"service": "opsight-api", "severity": "ERROR"},
                        "values": [["1715659916000000000", "{\"status_code\":503,\"message\":\"dependency unavailable\"}"]],
                    }
                ]
            },
        }

    async def tempo_trace(trace_id: str) -> dict[str, Any]:
        return {
            "batches": [
                {
                    "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "payment-gateway"}}]},
                    "scopeSpans": [
                        {
                            "spans": [
                                {
                                    "name": "authorize",
                                    "startTimeUnixNano": "1000000000",
                                    "endTimeUnixNano": "1900000000",
                                    "status": {"code": "STATUS_CODE_ERROR"},
                                }
                            ]
                        }
                    ],
                }
            ]
        }

    workflow.telemetry.prometheus_query = prometheus_query  # type: ignore[method-assign]
    workflow.telemetry.loki_query_range = loki_query_range  # type: ignore[method-assign]
    workflow.telemetry.tempo_trace = tempo_trace  # type: ignore[method-assign]

    try:
        result = await workflow.analyze_alertmanager_webhook(payload)

        assert result.received_alerts == 1
        assert result.analyses[0].provider == "rule_based"
        assert result.analyses[0].likely_root_causes[0].confidence == "high"
        assert "availability-99.9" in result.analyses[0].impacted_slos
        assert result.generated[0].incident_id == "slo-fast-burn-demo"
        assert Path(result.generated[0].json_path).exists()
        assert Path(result.generated[0].markdown_path).exists()
        artifact = json.loads(Path(result.generated[0].json_path).read_text(encoding="utf-8"))
        assert artifact["context"]["burn_rate"] == 120
        assert "status_code=503" in artifact["context"]["logs"]["patterns"]
        assert "payment-gateway authorize 900ms" in artifact["context"]["traces"]["slow_spans"]
    finally:
        shutil.rmtree(output, ignore_errors=True)


def _prometheus_value(value: float) -> dict[str, Any]:
    return {"status": "success", "data": {"result": [{"value": [1715659916.0, str(value)]}]}}
