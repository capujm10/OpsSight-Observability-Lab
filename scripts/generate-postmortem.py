#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from string import Template
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "incident-postmortems" / "examples"
DEFAULT_OUTPUT = ROOT / "incident-postmortems" / "generated"
DEFAULT_TEMPLATES = ROOT / "incident-postmortems" / "templates"


def parse_utc(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def format_timestamp(value: str) -> str:
    return parse_utc(value).strftime("%Y-%m-%d %H:%M UTC")


def format_timeline(events: list[dict[str, str]]) -> str:
    sorted_events = sorted(events, key=lambda event: parse_utc(event["timestamp"]))
    return "\n".join(f"- {format_timestamp(event['timestamp'])} - {event['event']}" for event in sorted_events)


def bullets(values: list[str]) -> str:
    if not values:
        return "- None recorded."
    return "\n".join(f"- {value}" for value in values)


def tasks(values: list[dict[str, str]]) -> str:
    if not values:
        return "| Task | Owner | Priority | Status |\n| --- | --- | --- | --- |\n| None recorded | - | - | - |"
    rows = ["| Task | Owner | Priority | Status |", "| --- | --- | --- | --- |"]
    for task in values:
        rows.append(
            f"| {task['task']} | {task.get('owner', 'Unassigned')} | "
            f"{task.get('priority', 'P2')} | {task.get('status', 'Open')} |"
        )
    return "\n".join(rows)


def telemetry_references(data: dict[str, Any]) -> str:
    refs = data.get("telemetry", {})
    sections = [
        "### Grafana Dashboards",
        bullets(refs.get("grafana_dashboards", [])),
        "",
        "### Prometheus Queries",
        bullets([f"`{query}`" for query in refs.get("prometheus_queries", [])]),
        "",
        "### Loki Queries",
        bullets([f"`{query}`" for query in refs.get("loki_queries", [])]),
        "",
        "### Tempo Trace References",
        bullets(refs.get("tempo_traces", [])),
        "",
        "### Correlation IDs",
        bullets(refs.get("correlation_ids", [])),
    ]
    return "\n".join(sections)


def ai_enrichment(data: dict[str, Any]) -> str:
    enrichment = data.get("ai_rca")
    if not enrichment:
        return (
            "## AI-Assisted RCA Enrichment\n\n"
            "No AI RCA enrichment was attached for this incident. Generate one through `apps/ai-rca` "
            "before final review if telemetry context is available."
        )

    hypotheses = enrichment.get("likely_root_causes", [])
    hypothesis_lines = []
    for index, hypothesis in enumerate(hypotheses, start=1):
        signals = bullets(hypothesis.get("supporting_signals", []))
        validation = bullets(hypothesis.get("validation_steps", []))
        hypothesis_lines.append(
            f"{index}. **{hypothesis['cause']}**\n"
            f"   - Confidence: {hypothesis.get('confidence', 'medium')}\n"
            f"   - Supporting telemetry:\n{signals}\n"
            f"   - Validation steps:\n{validation}"
        )

    sections = [
        "## AI-Assisted RCA Enrichment",
        "",
        "> AI-generated operational analysis. Validate against Prometheus, Loki, Tempo, deployment history, "
        "and incident commander notes before treating as final RCA.",
        "",
        "### AI Incident Summary",
        "",
        enrichment.get("summary", "No summary generated."),
        "",
        "### AI Telemetry Interpretation",
        "",
        enrichment.get("telemetry_interpretation", "No telemetry interpretation generated."),
        "",
        "### AI RCA Hypotheses",
        "",
        "\n\n".join(hypothesis_lines) if hypothesis_lines else "- No hypotheses generated.",
        "",
        "### AI Remediation Suggestions",
        "",
        bullets(enrichment.get("recommended_actions", [])),
        "",
        "### AI Risk Notes",
        "",
        bullets(enrichment.get("risk_notes", [])),
    ]
    return "\n".join(sections)


def annotation_json(data: dict[str, Any]) -> str:
    annotations = []
    for event in data.get("timeline", []):
        stage = event.get("stage")
        if stage not in {"incident_start", "mitigation_deployed", "recovery_confirmed"}:
            continue
        annotations.append(
            {
                "time": int(parse_utc(event["timestamp"]).timestamp() * 1000),
                "tags": ["opsight", data["severity"], stage, data["id"]],
                "text": event["event"],
            }
        )
    return json.dumps(annotations, indent=2, sort_keys=True)


def build_context(data: dict[str, Any]) -> dict[str, str]:
    started = parse_utc(data["started_at"])
    resolved_at = data.get("resolved_at")
    duration = "Unresolved"
    if resolved_at:
        minutes = round((parse_utc(resolved_at) - started).total_seconds() / 60)
        duration = f"{minutes} minutes"
    return {
        "id": data["id"],
        "title": data["title"],
        "severity": data["severity"],
        "status": data["status"],
        "type": data["type"],
        "started_at": format_timestamp(data["started_at"]),
        "resolved_at": format_timestamp(resolved_at) if resolved_at else "Unresolved",
        "duration": duration,
        "owner": data.get("owner", "On-call SRE"),
        "incident_commander": data.get("incident_commander", "Not assigned"),
        "impact_summary": data["impact_summary"],
        "affected_systems": bullets(data.get("affected_systems", [])),
        "customer_impact": data["customer_impact"],
        "timeline": format_timeline(data.get("timeline", [])),
        "detection_method": data["detection_method"],
        "alert_triggered": data["alert_triggered"],
        "slo_burn": data.get("slo_burn", "Not applicable"),
        "contributing_factors": bullets(data.get("contributing_factors", [])),
        "root_cause": data["root_cause"],
        "mitigation_steps": bullets(data.get("mitigation_steps", [])),
        "resolution": data["resolution"],
        "recovery_validation": bullets(data.get("recovery_validation", [])),
        "preventive_actions": bullets(data.get("preventive_actions", [])),
        "follow_up_tasks": tasks(data.get("follow_up_tasks", [])),
        "lessons_learned": bullets(data.get("lessons_learned", [])),
        "ai_enrichment": ai_enrichment(data),
        "telemetry_references": telemetry_references(data),
        "grafana_annotations": annotation_json(data),
    }


def render_incident(input_file: Path, template_dir: Path, output_dir: Path) -> Path:
    data = json.loads(input_file.read_text(encoding="utf-8"))
    template_path = template_dir / f"{data['template']}.md"
    template = Template(template_path.read_text(encoding="utf-8"))
    rendered = template.safe_substitute(build_context(data))
    slug = re.sub(r"[^a-z0-9]+", "-", data["title"].lower()).strip("-")
    output_path = output_dir / f"{data['id']}-{slug}.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate OpsSight incident postmortem drafts from structured incident data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--templates", type=Path, default=DEFAULT_TEMPLATES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    inputs = sorted(args.input.glob("*.json")) if args.input.is_dir() else [args.input]
    generated = [render_incident(path, args.templates, args.output) for path in inputs]
    for path in generated:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
