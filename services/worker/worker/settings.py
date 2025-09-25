"""Runtime configuration for the Temporal worker service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    host: str = "localhost:7233"
    namespace: str = "default"

    model_config = SettingsConfigDict(env_prefix="TEMPORAL_", case_sensitive=False)


settings = Settings()

__all__ = ["Settings", "settings"]
