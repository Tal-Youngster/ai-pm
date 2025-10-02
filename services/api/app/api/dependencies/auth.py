"""Authentication dependencies for FastAPI routes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Header, HTTPException, status

ALLOWED_ROLES = {"admin", "lead", "client"}
DEV_USER_HEADER = "x-dev-user"
DEV_ROLE_HEADER = "x-dev-roles"


def _parse_roles(raw_roles: str | None) -> list[str]:
    if not raw_roles:
        return ["client"]

    roles: list[str] = []
    for item in raw_roles.split(","):
        role = item.strip().lower()
        if role and role in ALLOWED_ROLES and role not in roles:
            roles.append(role)

    return roles or ["client"]


def _parse_dev_user_header(value: str) -> tuple[str, list[str]]:
    """Interpret a dev header value in the form `email|role1,role2`."""
    email_part, _, roles_part = value.partition("|")
    email = email_part.strip()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="x-dev-user header must include an email before the optional role list"
        )

    roles = _parse_roles(roles_part)
    return email, roles


def _validate_bearer_token(header_value: str) -> None:
    scheme, _, token = header_value.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bearer token verification not implemented"
    )


@dataclass(slots=True)
class AuthenticatedUser:
    """Simple representation of an authenticated user."""

    email: str
    roles: list[str]

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles


DevUserHeader = Annotated[str | None, Header(alias=DEV_USER_HEADER)]
DevRoleHeader = Annotated[str | None, Header(alias=DEV_ROLE_HEADER)]
AuthorizationHeader = Annotated[str | None, Header(alias="authorization")]


async def get_current_user(
    dev_user: DevUserHeader = None,
    dev_roles: DevRoleHeader = None,
    authorization: AuthorizationHeader = None
) -> AuthenticatedUser:
    """Return the current user or raise if auth cannot be established."""
    if dev_user:
        email, roles_from_user = _parse_dev_user_header(dev_user)
        roles = roles_from_user if dev_roles is None else _parse_roles(dev_roles)
        return AuthenticatedUser(email=email, roles=roles)

    if authorization:
        _validate_bearer_token(authorization)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


__all__ = ["AuthenticatedUser", "get_current_user"]
