"""Shared pytest fixtures for API service tests."""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest

from app.db.base import SessionLocal, engine
from app.db.models import Base, Organization, Persona, PersonaRole, Project, ProjectStatus


@pytest.fixture(autouse=True)
def prepare_database() -> Iterator[None]:
    """Recreate the database schema for every test to keep isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def project() -> Project:
    with SessionLocal() as session:
        organization = Organization(name="Test Org")
        session.add(organization)
        session.flush()

        project = Project(
            name="Test Project",
            description="Fixture project",
            organization_id=organization.id,
            status=ProjectStatus.ACTIVE,
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


@pytest.fixture
def persona_id(project: Project) -> uuid.UUID:
    with SessionLocal() as session:
        persona = Persona(
            project_id=project.id,
            role=PersonaRole.CLIENT,
            display_name="Primary Persona",
        )
        session.add(persona)
        session.commit()
        session.refresh(persona)
        return persona.id

