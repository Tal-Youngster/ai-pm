from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..utils import generate_id


class User(BaseModel):
    """Represents a platform user and their organization membership."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)

    id: str = Field(default_factory=generate_id, description="Unique user identifier")
    org_id: str = Field(..., description="Identifier of the owning organization")
    email: EmailStr = Field(..., description="Primary contact email")
    full_name: str | None = Field(None, description="Optional display name")
    is_active: bool = Field(default=True, description="Flag controlling login access")
    last_login_at: datetime | None = Field(
        default=None,
        description="Timestamp of the most recent successful authentication",
    )


__all__ = ["User"]
