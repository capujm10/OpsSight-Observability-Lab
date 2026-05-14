from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "payment-gateway"
    service_version: str = "1.0.0"
    environment: str = "local"
    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: str = "http://alloy:4317"
    base_latency_ms: int = 85
    failure_rate: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DEPENDENCY_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
