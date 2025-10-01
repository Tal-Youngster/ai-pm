from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .org import Org
from .project import Project
from .user import User


class BasicResponse(BaseModel):
    """Lightweight envelope returned by simple endpoints."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    message: str = Field(..., description="Human-readable summary of the result")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured payload with additional context",
    )


__all__ = ["Org", "User", "Project", "BasicResponse"]
