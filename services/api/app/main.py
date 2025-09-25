"""Application entrypoint for the ai-pm API service."""

from fastapi import FastAPI

from app.api import api_router
from app.config import Settings
from app.telemetry.otel import configure_telemetry


def create_app() -> FastAPI:
    """Create and configure a FastAPI application instance."""
    settings = Settings()
    application = FastAPI(title="ai-pm API", version="0.1.0")

    configure_telemetry(application, settings)

    @application.get("/healthz", tags=["health"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(api_router)

    return application


app = create_app()
