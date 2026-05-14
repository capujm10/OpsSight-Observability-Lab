#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "apps" / "ai-rca" / "tests" / "fixtures" / "alertmanager-slo-fast-burn.json"


def main() -> int:
    endpoint = os.getenv("AI_RCA_ALERT_WEBHOOK_URL", "http://localhost:8090/api/v1/alertmanager/webhook")
    fixture = Path(os.getenv("AI_RCA_ALERT_FIXTURE", str(DEFAULT_FIXTURE)))
    payload = fixture.read_bytes()
    request = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        print(json.dumps(json.loads(response.read().decode("utf-8")), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
