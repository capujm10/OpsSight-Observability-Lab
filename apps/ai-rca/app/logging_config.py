import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.request_context import correlation_id_ctx, trace_id_ctx


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": record.levelname,
            "service": "opsight-ai-rca",
            "component": getattr(record, "component", record.name),
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get(),
            "trace_id": trace_id_ctx.get(),
            "logger": record.name,
        }
        for key in (
            "provider",
            "model",
            "workflow",
            "outcome",
            "duration_ms",
            "fallback_reason",
            "alert_name",
            "incident_id",
        ):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    logging.getLogger("uvicorn.access").disabled = True
