"""Project management endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models import (
    Client,
    Organization,
    Persona,
    PersonaRole,
    Project,
    ProjectStatus,
    Requirement,
    RequirementType,
    User,
)

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    """Payload for creating a project."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    organization_id: int
    client_id: int | None = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)


class ProjectUpdate(BaseModel):
    """Payload for updating mutable project fields."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: ProjectStatus | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "ProjectUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class ProjectBaseResponse(BaseModel):
    """Shared attributes describing a project."""

    id: int
    name: str
    description: str | None
    status: ProjectStatus
    organization_id: int
    client_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectSummaryResponse(ProjectBaseResponse):
    """Project listing payload with aggregate relationships."""

    persona_count: int
    requirement_count: int


class RequirementCounts(BaseModel):
    """Requirement rollups for a project."""

    total: int
    by_type: dict[str, int]


class PersonaSummary(BaseModel):
    """Lightweight persona representation for project views."""

    id: UUID
    role: PersonaRole
    display_name: str

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectBaseResponse):
    """Detailed project payload including linked personas and requirement counts."""

    personas: list[PersonaSummary]
    requirement_counts: RequirementCounts


def _ensure_organization_exists(session: Session, organization_id: int) -> None:
    if session.get(Organization, organization_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")


def _ensure_client_association(session: Session, client_id: int | None, organization_id: int) -> None:
    if client_id is None:
        return
    client = session.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    if client.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client does not belong to the specified organization",
        )


def _ensure_user_exists(session: Session, user_id: int) -> None:
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


def _get_project_or_404(session: Session, project_id: int) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _project_base_dict(project: Project) -> dict[str, Any]:
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "organization_id": project.organization_id,
        "client_id": project.client_id,
        "created_at": project.created_at,
    }


def _calculate_requirement_counts(session: Session, project_id: int) -> RequirementCounts:
    rows = session.execute(
        select(Requirement.type, func.count(Requirement.id))
        .where(Requirement.project_id == project_id)
        .group_by(Requirement.type)
    ).all()

    by_type: dict[str, int] = {}
    for requirement_type, count in rows:
        if isinstance(requirement_type, RequirementType):
            key = requirement_type.value
        else:
            key = str(requirement_type)
        by_type[key] = count

    total = sum(by_type.values())
    return RequirementCounts(total=total, by_type=by_type)


def _build_project_detail(session: Session, project: Project) -> ProjectDetailResponse:
    base = _project_base_dict(project)
    personas = [PersonaSummary.model_validate(persona) for persona in project.personas]
    requirement_counts = _calculate_requirement_counts(session, project.id)

    return ProjectDetailResponse(
        **base,
        personas=personas,
        requirement_counts=requirement_counts,
    )


def _build_project_summary(project: Project, persona_count: int, requirement_count: int) -> ProjectSummaryResponse:
    base = _project_base_dict(project)
    return ProjectSummaryResponse(
        **base,
        persona_count=persona_count,
        requirement_count=requirement_count,
    )


@router.post("", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, session: Session = Depends(get_session)) -> ProjectDetailResponse:
    """Create a project within an organization."""
    _ensure_organization_exists(session, payload.organization_id)
    _ensure_client_association(session, payload.client_id, payload.organization_id)

    project = Project(
        name=payload.name,
        description=payload.description,
        organization_id=payload.organization_id,
        client_id=payload.client_id,
        status=payload.status,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return _build_project_detail(session, project)


@router.get("", response_model=list[ProjectSummaryResponse])
def list_projects(
    organization_id: int = Query(..., description="Organization identifier to filter projects."),
    client_id: int | None = Query(default=None, description="Optional client filter."),
    user_id: int | None = Query(default=None, description="Optional user filter via persona assignments."),
    session: Session = Depends(get_session),
) -> list[ProjectSummaryResponse]:
    """List projects for an organization with optional client or user filtering."""
    _ensure_organization_exists(session, organization_id)
    _ensure_client_association(session, client_id, organization_id)
    if user_id is not None:
        _ensure_user_exists(session, user_id)

    persona_counts = (
        select(Persona.project_id, func.count(Persona.id).label("persona_count"))
        .group_by(Persona.project_id)
        .subquery()
    )
    requirement_counts = (
        select(Requirement.project_id, func.count(Requirement.id).label("requirement_count"))
        .group_by(Requirement.project_id)
        .subquery()
    )

    stmt = (
        select(
            Project,
            func.coalesce(persona_counts.c.persona_count, 0),
            func.coalesce(requirement_counts.c.requirement_count, 0),
        )
        .outerjoin(persona_counts, persona_counts.c.project_id == Project.id)
        .outerjoin(requirement_counts, requirement_counts.c.project_id == Project.id)
        .where(Project.organization_id == organization_id)
    )

    if client_id is not None:
        stmt = stmt.where(Project.client_id == client_id)

    if user_id is not None:
        stmt = stmt.where(
            Project.id.in_(select(Persona.project_id).where(Persona.user_id == user_id))
        )

    stmt = stmt.order_by(Project.created_at.asc())
    rows = session.execute(stmt).all()

    return [
        _build_project_summary(project, persona_count or 0, requirement_count or 0)
        for project, persona_count, requirement_count in rows
    ]


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: int, session: Session = Depends(get_session)) -> ProjectDetailResponse:
    """Fetch project details including personas and requirement rollups."""
    project = _get_project_or_404(session, project_id)
    return _build_project_detail(session, project)


@router.patch("/{project_id}", response_model=ProjectDetailResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    session: Session = Depends(get_session),
) -> ProjectDetailResponse:
    """Update a project's mutable fields."""
    project = _get_project_or_404(session, project_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "name" in update_data:
        project.name = update_data["name"]
    if "description" in update_data:
        project.description = update_data["description"]
    if "status" in update_data:
        project.status = update_data["status"]

    session.add(project)
    session.commit()
    session.refresh(project)
    return _build_project_detail(session, project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_project(project_id: int, session: Session = Depends(get_session)) -> Response:
    """Remove a project and cascade related data."""
    project = _get_project_or_404(session, project_id)

    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


