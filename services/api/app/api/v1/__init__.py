"""Version 1 of the public API."""

from fastapi import APIRouter

from app.api.v1 import health

router = APIRouter()
router.include_router(health.router, tags=["health"])

__all__ = ["router"]
