from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..utils import generate_id


class Org(BaseModel):
    """Represents a tenant organization within the ai-pm platform."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)

    id: str = Field(default_factory=generate_id, description="Unique organization identifier")
    name: str = Field(..., min_length=1, description="Human-readable organization name")
    slug: str | None = Field(None, description="URL-friendly slug for the organization")
    created_at: datetime | None = Field(
        default=None,
        description="Optional creation timestamp supplied by the persistence layer",
    )


__all__ = ["Org"]
