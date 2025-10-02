"""Application configuration powered by Pydantic settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from the environment."""

    database_url: str = Field(
        default="sqlite:///./app.db",
        alias="DATABASE_URL",
        description="Database connection string.",
    )
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        alias="OTEL_EXPORTER_OTLP_ENDPOINT",
        description="Endpoint for OTLP trace exporter.",
    )
    environment: str = Field(
        default="development",
        alias="ENVIRONMENT",
        description="Deployment environment name.",
    )
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
        alias="CORS_ALLOW_ORIGINS",
        description="Allowed origins for CORS requests.",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

