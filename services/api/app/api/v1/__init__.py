"""Version 1 of the public API."""

from fastapi import APIRouter

from app.api.v1 import auth, health, intake, personas, projects, requirements

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router)
router.include_router(intake.router)
router.include_router(personas.router)
router.include_router(projects.router)
router.include_router(requirements.router)

__all__ = ["router"]
