import logging
from typing import Any

import httpx

from app.config import Settings

logger = logging.getLogger("ai-rca.telemetry")


class TelemetryClients:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def prometheus_query(self, query: str) -> dict[str, Any]:
        return await self._get_json(f"{self.settings.prometheus_url.rstrip('/')}/api/v1/query", {"query": query}, "prometheus")

    async def loki_query(self, query: str, limit: int = 20) -> dict[str, Any]:
        return await self._get_json(
            f"{self.settings.loki_url.rstrip('/')}/loki/api/v1/query",
            {"query": query, "limit": str(limit)},
            "loki",
        )

    async def loki_query_range(self, query: str, limit: int = 20) -> dict[str, Any]:
        return await self._get_json(
            f"{self.settings.loki_url.rstrip('/')}/loki/api/v1/query_range",
            {"query": query, "limit": str(limit)},
            "loki",
        )

    async def tempo_trace(self, trace_id: str) -> dict[str, Any]:
        return await self._get_json(f"{self.settings.tempo_url.rstrip('/')}/api/traces/{trace_id}", {}, "tempo")

    async def _get_json(self, url: str, params: dict[str, str], backend: str) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            logger.warning("telemetry backend unavailable", extra={"component": backend, "outcome": "degraded"}, exc_info=exc)
            return {"status": "unavailable", "backend": backend, "error": str(exc)}
