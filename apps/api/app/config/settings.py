from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "opsight-api"
    service_version: str = "1.0.0"
    environment: str = "local"
    log_level: str = "INFO"
    otel_enabled: bool = True
    otel_exporter_otlp_endpoint: str = "http://alloy:4317"
    readiness_dependency_enabled: bool = True
    dependency_url: str = "http://dependency:8080"
    dependency_timeout_seconds: float = Field(default=2.0, gt=0, le=30)
    latency_simulation_ms: int = Field(default=1500, ge=0, le=30000)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="OPSIGHT_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
