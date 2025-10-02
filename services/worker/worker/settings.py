"""Runtime configuration for the Temporal worker service."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    host: str = "localhost:7233"
    namespace: str = "default"
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        alias="OTEL_EXPORTER_OTLP_ENDPOINT",
        description="Target OTLP endpoint for span export.",
    )
    environment: str = Field(
        default="development",
        alias="ENVIRONMENT",
        description="Deployment environment name.",
    )

    model_config = SettingsConfigDict(env_prefix="TEMPORAL_", case_sensitive=False)


settings = Settings()

__all__ = ["Settings", "settings"]
