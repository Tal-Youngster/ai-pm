"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    """Simple heartbeat endpoint for monitoring."""
    return {"status": "ok"}
