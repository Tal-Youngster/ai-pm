"""Authentication endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/callback")
async def auth_callback(state: str | None = None, code: str | None = None) -> dict[str, str | None]:
    """Placeholder endpoint for OAuth callbacks."""
    return {
        "status": "pending",
        "detail": "OAuth callback handling not implemented",
        "state": state,
        "code": code,
    }


@router.get("/me")
async def read_current_user(current_user: AuthenticatedUser = Depends(get_current_user)) -> dict[str, object]:
    """Return the authenticated user when available."""
    return {
        "email": current_user.email,
        "roles": current_user.roles,
        "is_admin": current_user.is_admin,
    }
