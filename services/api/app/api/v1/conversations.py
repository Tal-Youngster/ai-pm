"""Conversation management endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models import ConversationTurn, Persona, Project

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationTurnCreate(BaseModel):
    """Payload for recording a conversation turn."""

    project_id: int
    persona_id: UUID
    text: str = Field(min_length=1)


class ConversationTurnResponse(BaseModel):
    """Serialized conversation turn representation."""

    id: UUID
    project_id: int
    persona_id: UUID
    text: str
    embedding: list[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("embedding")
    def serialize_embedding(self, embedding: list[float]) -> list[float]:
        return list(embedding)


def _ensure_project_exists(session: Session, project_id: int) -> None:
    if session.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


def _get_persona(session: Session, persona_id: UUID) -> Persona:
    persona = session.get(Persona, persona_id)
    if persona is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return persona


def _generate_embedding_stub(text: str) -> list[float]:
    """Return a deterministic embedding placeholder until model integration exists."""
    normalized = float(len(text))
    checksum = sum(ord(char) for char in text) % 1000
    return [normalized, float(checksum), 0.0]


@router.post("", response_model=ConversationTurnResponse, status_code=status.HTTP_201_CREATED)
def create_conversation_turn(
    payload: ConversationTurnCreate, session: Session = Depends(get_session)
) -> ConversationTurn:
    """Record a new conversation turn for a project."""
    _ensure_project_exists(session, payload.project_id)
    persona = _get_persona(session, payload.persona_id)
    if persona.project_id != payload.project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Persona does not belong to the provided project",
        )

    conversation_turn = ConversationTurn(
        project_id=payload.project_id,
        persona_id=payload.persona_id,
        text=payload.text,
        embedding=_generate_embedding_stub(payload.text),
    )
    session.add(conversation_turn)
    session.commit()
    session.refresh(conversation_turn)
    return conversation_turn


@router.get("", response_model=list[ConversationTurnResponse])
def list_conversation_turns(
    project_id: int = Query(..., description="Project identifier to filter conversation turns."),
    persona_id: UUID | None = Query(default=None, description="Optional persona filter."),
    session: Session = Depends(get_session),
) -> list[ConversationTurn]:
    """Return conversation turns for a project with optional persona filtering."""
    _ensure_project_exists(session, project_id)

    stmt = select(ConversationTurn).where(ConversationTurn.project_id == project_id)
    if persona_id is not None:
        stmt = stmt.where(ConversationTurn.persona_id == persona_id)
    stmt = stmt.order_by(ConversationTurn.created_at.asc())

    return list(session.scalars(stmt).all())
