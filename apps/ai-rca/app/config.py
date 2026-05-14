from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ProviderMode = Literal["ollama", "lmstudio", "openai_compatible", "rule_based"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    service_name: str = "opsight-ai-rca"
    service_version: str = "0.3.0"
    environment: str = Field(default="local", alias="OPSIGHT_ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="AI_RCA_LOG_LEVEL")
    otel_exporter_otlp_endpoint: str = Field(default="http://alloy:4317", alias="OPSIGHT_OTEL_EXPORTER_OTLP_ENDPOINT")

    ai_provider: ProviderMode = Field(default="rule_based", alias="AI_PROVIDER")
    ai_model: str = Field(default="llama3.2", alias="AI_MODEL")
    ai_base_url: str = Field(default="http://localhost:11434", alias="AI_BASE_URL")
    ai_api_key: str | None = Field(default=None, alias="AI_API_KEY")
    ai_timeout_seconds: float = Field(default=30, gt=0, le=300, alias="AI_TIMEOUT_SECONDS")
    ai_max_input_chars: int = Field(default=12000, ge=1000, le=100000, alias="AI_MAX_INPUT_CHARS")
    ai_max_output_tokens: int = Field(default=800, ge=64, le=8192, alias="AI_MAX_OUTPUT_TOKENS")

    prometheus_url: str = Field(default="http://prometheus:9090", alias="PROMETHEUS_URL")
    loki_url: str = Field(default="http://loki:3100", alias="LOKI_URL")
    tempo_url: str = Field(default="http://tempo:3200", alias="TEMPO_URL")
    grafana_url: str = Field(default="http://localhost:3000", alias="GRAFANA_URL")
    artifact_dir: str = Field(default="artifacts/ai-rca", alias="AI_RCA_ARTIFACT_DIR")


@lru_cache
def get_settings() -> Settings:
    return Settings()
