#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.request


def main() -> int:
    endpoint = os.getenv("AI_RCA_URL", "http://localhost:8090/api/v1/rca/analyze")
    payload = {
        "incident_id": "INC-DEMO-AI-RCA",
        "title": "Payment gateway dependency degradation causing order API failures",
        "affected_services": ["opsight-api", "payment-gateway"],
        "impacted_slos": ["availability-99.9", "api-p95-latency"],
        "burn_rate": 120,
        "error_rate": 0.12,
        "p95_latency_seconds": 1.8,
        "dependency": "payment-gateway",
        "alert": {
            "name": "OpsSightSLOFastBurn",
            "severity": "critical",
            "service": "opsight-api",
            "summary": "Availability SLO fast burn detected",
        },
        "traces": {
            "trace_ids": ["27a51aae7664ac0c0708c9af0ec80334"],
            "slow_spans": ["opsight-api -> payment-gateway authorize"],
            "failed_spans": ["payment-gateway authorize 503"],
            "services": ["opsight-api", "payment-gateway"],
        },
        "logs": {
            "correlation_ids": ["trace-chain-check"],
            "patterns": ["dependency_unavailable", "status_code=503"],
            "exception_signatures": ["DownstreamDependencyUnavailable"],
            "loki_queries": [
                '{service="opsight-api",severity="ERROR"} | json',
                '{service="payment-gateway"} | json | outcome="failure"',
            ],
        },
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=20) as response:
        print(json.dumps(json.loads(response.read().decode("utf-8")), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
