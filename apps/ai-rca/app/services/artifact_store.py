import json
import re
from datetime import UTC, datetime
from pathlib import Path

from app.models.rca import IncidentContext, RCAArtifact, RCAResponse


class RCAArtifactStore:
    def __init__(self, artifact_dir: str) -> None:
        self.root = Path(artifact_dir)

    def persist(self, context: IncidentContext, response: RCAResponse) -> RCAArtifact:
        incident_id = context.incident_id or f"alert-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", incident_id).strip("-")
        self.root.mkdir(parents=True, exist_ok=True)
        json_path = self.root / f"{safe_id}.json"
        markdown_path = self.root / f"{safe_id}.md"
        payload = {"context": context.model_dump(mode="json"), "rca": response.model_dump(mode="json")}
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        markdown_path.write_text(_markdown(context, response), encoding="utf-8")
        return RCAArtifact(incident_id=incident_id, json_path=str(json_path), markdown_path=str(markdown_path))


def _markdown(context: IncidentContext, response: RCAResponse) -> str:
    alert = context.alert
    lines = [
        f"# AI RCA Artifact: {context.title or (alert.name if alert else context.incident_id)}",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Incident ID | `{context.incident_id or '-'}` |",
        f"| Alert | `{alert.name if alert else '-'}` |",
        f"| Status | `{alert.status if alert else '-'}` |",
        f"| Severity | `{alert.severity if alert else '-'}` |",
        f"| Service | `{alert.service if alert else ', '.join(context.affected_services)}` |",
        f"| Fingerprint | `{alert.fingerprint if alert else '-'}` |",
        f"| Provider | `{response.provider}` |",
        f"| Model | `{response.model}` |",
        f"| Fallback Used | `{response.fallback_used}` |",
        "",
        "## Summary",
        "",
        response.summary,
        "",
        "## Alert Explanation",
        "",
        response.alert_explanation,
        "",
        "## Trace Analysis",
        "",
        response.trace_analysis,
        "",
        "## Log Analysis",
        "",
        response.log_analysis,
        "",
        "## Ranked RCA Hypotheses",
        "",
    ]
    for index, cause in enumerate(response.likely_root_causes, start=1):
        lines.extend(
            [
                f"{index}. **{cause.cause}**",
                f"   - Confidence: {cause.confidence}",
                f"   - Impacted systems: {', '.join(cause.impacted_systems)}",
                f"   - Supporting signals: {', '.join(cause.supporting_signals)}",
                f"   - Validation steps: {', '.join(cause.validation_steps)}",
            ]
        )
    lines.extend(
        [
            "",
            "## Recommended Actions",
            "",
            *[f"- {action}" for action in response.recommended_actions],
            "",
            "## Telemetry References",
            "",
        ]
    )
    for name, values in response.telemetry_references.items():
        lines.append(f"### {name}")
        lines.extend(f"- `{value}`" for value in values)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
