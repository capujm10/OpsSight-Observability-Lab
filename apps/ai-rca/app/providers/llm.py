import json
import logging
import time
from typing import Any

import httpx

from app.config import Settings
from app.models.rca import IncidentContext, RCAResponse
from app.providers.base import AIProvider, ProviderResult
from app.providers.rule_based import RuleBasedProvider
from app.telemetry.metrics import AI_RCA_PROVIDER_FAILURES_TOTAL

logger = logging.getLogger("ai-rca.provider")


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = settings.ai_model

    async def generate_rca(self, context: IncidentContext, prompt: str) -> ProviderResult:
        url = f"{self.settings.ai_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"num_predict": self.settings.ai_max_output_tokens, "temperature": 0.1},
        }
        return await _post_llm(url, payload, self.name, self.model, self.settings, context, prompt)


class OpenAICompatibleProvider(AIProvider):
    def __init__(self, settings: Settings, name: str) -> None:
        self.settings = settings
        self.name = name
        self.model = settings.ai_model

    async def generate_rca(self, context: IncidentContext, prompt: str) -> ProviderResult:
        url = f"{self.settings.ai_base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}"} if self.settings.ai_api_key else {}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an SRE incident analysis assistant. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": self.settings.ai_max_output_tokens,
        }
        return await _post_llm(url, payload, self.name, self.model, self.settings, context, prompt, headers)


async def _post_llm(
    url: str,
    payload: dict[str, Any],
    provider: str,
    model: str,
    settings: Settings,
    context: IncidentContext,
    prompt: str,
    headers: dict[str, str] | None = None,
) -> ProviderResult:
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
        content = body.get("response") or body.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        parsed = json.loads(content)
        rca = RCAResponse(
            summary=parsed.get("summary", "LLM returned no summary."),
            alert_explanation=parsed.get("alert_explanation", "No alert explanation returned."),
            trace_analysis=parsed.get("trace_analysis", "No trace analysis returned."),
            log_analysis=parsed.get("log_analysis", "No log analysis returned."),
            likely_root_causes=parsed.get("likely_root_causes", []),
            impacted_slos=parsed.get("impacted_slos", []),
            recommended_actions=parsed.get("recommended_actions", []),
            risk_notes=parsed.get("risk_notes", ["Validate AI output against telemetry before action."]),
            telemetry_references=parsed.get("telemetry_references", {}),
            provider=provider,
            model=model,
            fallback_used=False,
            confidence=parsed.get("confidence", "medium"),
        )
        return ProviderResult(
            response=rca,
            prompt_tokens=body.get("prompt_eval_count", max(1, round(len(prompt) / 4))),
            completion_tokens=body.get("eval_count", max(1, round(len(content) / 4))),
        )
    except Exception as exc:
        AI_RCA_PROVIDER_FAILURES_TOTAL.labels(provider=provider, reason=exc.__class__.__name__).inc()
        logger.warning(
            "llm provider unavailable; falling back to deterministic rule based rca",
            extra={"provider": provider, "model": model, "fallback_reason": exc.__class__.__name__},
        )
        result = await RuleBasedProvider().generate_rca(context, prompt)
        result.response.fallback_used = True
        result.response.provider = "rule_based"
        result.fallback_used = True
        result.completion_tokens = max(result.completion_tokens, round((time.perf_counter() - started) * 100))
        return result
