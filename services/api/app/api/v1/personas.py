"""Persona management endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models import Persona, PersonaRole, Project, User

router = APIRouter(prefix="/personas", tags=["personas"])


class PersonaCreate(BaseModel):
    """Payload for creating a persona."""

    project_id: int
    role: PersonaRole
    display_name: str = Field(min_length=1, max_length=255)
    user_id: int | None = None


class PersonaUpdate(BaseModel):
    """Payload for updating mutable persona fields."""

    role: PersonaRole | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def validate_payload(self) -> "PersonaUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class PersonaResponse(BaseModel):
    """Serialized persona representation."""

    id: UUID
    project_id: int
    user_id: int | None
    role: PersonaRole
    display_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


def _ensure_project_exists(session: Session, project_id: int) -> None:
    if session.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


def _ensure_user_exists(session: Session, user_id: int | None) -> None:
    if user_id is None:
        return
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


def _get_persona_or_404(session: Session, persona_id: UUID) -> Persona:
    persona = session.get(Persona, persona_id)
    if persona is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return persona


@router.post("", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
def create_persona(payload: PersonaCreate, session: Session = Depends(get_session)) -> Persona:
    """Create a persona for a project."""
    _ensure_project_exists(session, payload.project_id)
    _ensure_user_exists(session, payload.user_id)

    persona = Persona(
        project_id=payload.project_id,
        user_id=payload.user_id,
        role=payload.role,
        display_name=payload.display_name,
    )
    session.add(persona)
    session.commit()
    session.refresh(persona)
    return persona


@router.get("", response_model=list[PersonaResponse])
def list_personas(
    project_id: int = Query(..., description="Project identifier to filter personas."),
    session: Session = Depends(get_session),
) -> list[Persona]:
    """List personas associated with a project."""
    _ensure_project_exists(session, project_id)

    stmt = select(Persona).where(Persona.project_id == project_id).order_by(Persona.created_at.asc())
    return list(session.scalars(stmt).all())


@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona(persona_id: UUID, session: Session = Depends(get_session)) -> Persona:
    """Retrieve a persona by identifier."""
    return _get_persona_or_404(session, persona_id)


@router.patch("/{persona_id}", response_model=PersonaResponse)
def update_persona(
    persona_id: UUID,
    payload: PersonaUpdate,
    session: Session = Depends(get_session),
) -> Persona:
    """Update mutable persona fields."""
    persona = _get_persona_or_404(session, persona_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "role" in update_data:
        persona.role = update_data["role"]
    if "display_name" in update_data:
        persona.display_name = update_data["display_name"]

    session.add(persona)
    session.commit()
    session.refresh(persona)
    return persona


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_persona(persona_id: UUID, session: Session = Depends(get_session)) -> Response:
    """Delete a persona and cascade related artifacts."""
    persona = _get_persona_or_404(session, persona_id)

    session.delete(persona)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
