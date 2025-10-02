"""Requirement management endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models import Project, Requirement, RequirementType

router = APIRouter(prefix="/requirements", tags=["requirements"])


class RequirementCreate(BaseModel):
    """Payload for creating a requirement."""

    project_id: int
    persona_id: UUID
    text: str = Field(min_length=1)
    type: RequirementType
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    cluster_id: UUID | None = None


class RequirementUpdate(BaseModel):
    """Payload for updating a requirement."""

    type: RequirementType | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_payload(self) -> "RequirementUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class RequirementResponse(BaseModel):
    """Serialized requirement representation."""

    id: UUID
    project_id: int
    persona_id: UUID
    text: str
    type: RequirementType
    confidence: float | None
    cluster_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


def _ensure_project_exists(session: Session, project_id: int) -> None:
    if session.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


def _ensure_persona_exists(session: Session, persona_id: UUID) -> None:
    persona_exists = session.execute(
        text("SELECT 1 FROM personas WHERE id = :persona_id LIMIT 1"),
        {"persona_id": str(persona_id)},
    ).scalar()
    if persona_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")


@router.post("", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
def create_requirement(payload: RequirementCreate, session: Session = Depends(get_session)) -> Requirement:
    """Create a new requirement for a project persona pair."""
    _ensure_project_exists(session, payload.project_id)
    _ensure_persona_exists(session, payload.persona_id)

    requirement = Requirement(
        project_id=payload.project_id,
        persona_id=payload.persona_id,
        text=payload.text,
        type=payload.type,
        confidence=payload.confidence,
        cluster_id=payload.cluster_id,
    )
    session.add(requirement)
    session.commit()
    session.refresh(requirement)
    return requirement


@router.get("", response_model=list[RequirementResponse])
def list_requirements(
    project_id: int = Query(..., description="Project identifier to filter requirements."),
    persona_id: UUID | None = Query(default=None, description="Optional persona filter."),
    session: Session = Depends(get_session),
) -> list[Requirement]:
    """Return requirements for a project with optional persona filtering."""
    stmt = select(Requirement).where(Requirement.project_id == project_id)
    if persona_id is not None:
        stmt = stmt.where(Requirement.persona_id == persona_id)
    stmt = stmt.order_by(Requirement.created_at.asc())

    return list(session.execute(stmt).scalars().all())


@router.patch("/{requirement_id}", response_model=RequirementResponse)
def update_requirement(
    requirement_id: UUID,
    payload: RequirementUpdate,
    session: Session = Depends(get_session),
) -> Requirement:
    """Update an existing requirement's type or confidence."""
    requirement = session.get(Requirement, requirement_id)
    if requirement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(requirement, field, value)

    session.add(requirement)
    session.commit()
    session.refresh(requirement)
    return requirement


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_requirement(requirement_id: UUID, session: Session = Depends(get_session)) -> Response:
    """Remove a requirement by identifier."""
    requirement = session.get(Requirement, requirement_id)
    if requirement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    session.delete(requirement)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
