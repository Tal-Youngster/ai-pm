from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..utils import generate_id


class Project(BaseModel):
    """Represents a project tracked inside the ai-pm platform."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)

    id: str = Field(default_factory=generate_id, description="Unique project identifier")
    org_id: str = Field(..., description="Identifier of the owning organization")
    name: str = Field(..., min_length=1, description="Display name of the project")
    description: str | None = Field(None, description="Optional extended description")
    owner_user_id: str | None = Field(None, description="User primarily responsible for the project")
    created_at: datetime | None = Field(
        default=None,
        description="Creation timestamp provided by the persistence layer",
    )


__all__ = ["Project"]
