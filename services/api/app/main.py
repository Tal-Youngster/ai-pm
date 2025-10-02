"""Application entrypoint for the ai-pm API service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import Settings
from app.telemetry.otel import configure_telemetry
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator


def create_app() -> FastAPI:
    """Create and configure a FastAPI application instance."""
    settings = Settings()
    application = FastAPI(title="ai-pm API", version="0.1.0")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    configure_telemetry(application, settings)
    PrometheusFastApiInstrumentator().instrument(application).expose(application)

    @application.get("/healthz", tags=["health"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(api_router)

    return application


app = create_app()

