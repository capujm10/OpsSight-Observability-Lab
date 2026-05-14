import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-postmortem.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_postmortem", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_postmortems_include_required_operational_sections() -> None:
    generator = load_generator()
    output = ROOT / ".tmp-postmortem-tests"
    if output.exists():
        shutil.rmtree(output)
    report = generator.render_incident(
        ROOT / "incident-postmortems" / "examples" / "INC-2026-05-14-001-dependency-degradation.json",
        ROOT / "incident-postmortems" / "templates",
        output,
    )
    try:
        text = report.read_text(encoding="utf-8")
        required = [
            "## Timeline",
            "## Dependency Root Cause",
            "## Recovery Validation",
            "## Telemetry References",
            "### Loki Queries",
            "### Tempo Trace References",
            "Grafana Operational Annotations",
        ]
        for section in required:
            assert section in text
        assert "2026-05-14 04:08 UTC" in text
        assert "trace_id=27a51aae7664ac0c0708c9af0ec80334" in text
    finally:
        shutil.rmtree(output, ignore_errors=True)


def test_annotation_payload_contains_lifecycle_events() -> None:
    generator = load_generator()
    data = json.loads(
        (ROOT / "incident-postmortems" / "examples" / "INC-2026-05-14-001-dependency-degradation.json").read_text(encoding="utf-8")
    )
    annotations = json.loads(generator.annotation_json(data))
    tags = {tag for annotation in annotations for tag in annotation["tags"]}
    assert "incident_start" in tags
    assert "mitigation_deployed" in tags
    assert "recovery_confirmed" in tags
