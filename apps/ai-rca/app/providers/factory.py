from app.config import Settings
from app.providers.base import AIProvider
from app.providers.llm import OllamaProvider, OpenAICompatibleProvider
from app.providers.rule_based import RuleBasedProvider


def build_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "rule_based":
        return RuleBasedProvider()
    if settings.ai_provider == "ollama":
        return OllamaProvider(settings)
    if settings.ai_provider == "lmstudio":
        return OpenAICompatibleProvider(settings, "lmstudio")
    return OpenAICompatibleProvider(settings, "openai_compatible")
