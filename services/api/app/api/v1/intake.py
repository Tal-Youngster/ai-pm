"""Intake endpoints for converting raw text into requirements."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.api.v1.requirements import RequirementResponse
from app.db.base import get_session
from app.db.models import Persona, Project, Requirement, RequirementType

router = APIRouter(prefix="/intake", tags=["intake"])


class IntakeExtractPayload(BaseModel):
    """Incoming request body for requirement extraction."""

    project_id: int
    persona_id: UUID
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def _ensure_non_empty_text(self) -> "IntakeExtractPayload":
        if not self.text.strip():
            raise ValueError("text must contain non-whitespace characters")
        return self


class ExtractedRequirement(BaseModel):
    """Structured requirement returned by the stub extractor."""

    text: str = Field(min_length=1)
    type: RequirementType = RequirementType.FEATURE
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


def _ensure_project_exists(session: Session, project_id: int) -> None:
    if session.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


def _ensure_persona_exists(session: Session, persona_id: UUID) -> None:
    if session.get(Persona, persona_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")


def _extract_requirements_stub(text: str) -> list[ExtractedRequirement]:
    """Stubbed requirement extractor that splits non-empty lines into requirements."""
    segments: Iterable[str] = (
        segment.strip(" -\u2022")
        for segment in text.replace("\r", "").splitlines()
    )
    cleaned = [segment for segment in segments if segment]
    if not cleaned:
        cleaned = [text.strip()]

    return [ExtractedRequirement(text=segment) for segment in cleaned if segment]


@router.post(
    "/extract",
    response_model=list[RequirementResponse],
    status_code=status.HTTP_201_CREATED,
)
def extract_requirements(
    payload: IntakeExtractPayload,
    session: Session = Depends(get_session),
) -> list[Requirement]:
    """Convert raw text into requirements and persist them for the given persona."""
    _ensure_project_exists(session, payload.project_id)
    _ensure_persona_exists(session, payload.persona_id)

    extracted = _extract_requirements_stub(payload.text)
    if not extracted:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unable to extract requirements")

    saved: list[Requirement] = []
    for requirement in extracted:
        instance = Requirement(
            project_id=payload.project_id,
            persona_id=payload.persona_id,
            text=requirement.text,
            type=requirement.type,
            confidence=requirement.confidence,
        )
        session.add(instance)
        saved.append(instance)

    session.commit()
    for requirement in saved:
        session.refresh(requirement)

    return saved