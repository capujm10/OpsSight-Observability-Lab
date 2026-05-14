import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.config.settings import Settings
from app.log_context.context import correlation_id_ctx, trace_id_ctx


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        trace_id = trace_id_ctx.get()
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": record.levelname,
            "service": "opsight-api",
            "component": getattr(record, "component", record.name),
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get(),
            "trace_id": trace_id,
            "trace_url": (
                "http://localhost:3000/explore?schemaVersion=1&panes=%7B%7D&orgId=1&left="
                f"%7B%22datasource%22:%22tempo%22,%22queries%22:%5B%7B%22query%22:%22{trace_id}%22,"
                "%22queryType%22:%22traceId%22%7D%5D%7D"
            ),
            "logger": record.name,
        }
        for key in ("method", "path", "status_code", "duration_ms", "client_ip", "order_id", "scenario"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(settings: Settings) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())
    logging.getLogger("uvicorn.access").disabled = True
