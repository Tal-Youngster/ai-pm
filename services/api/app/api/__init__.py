"""API router configuration."""

from fastapi import APIRouter

from app.api.v1 import router as v1_router

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1", tags=["v1"])

__all__ = ["api_router"]
