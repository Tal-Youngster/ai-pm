"""SQLAlchemy models for core domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for ORM models."""


class RequirementType(str, Enum):
    """Requirement classification categories."""

    FEATURE = "feature"
    BUG = "bug"
    IMPROVEMENT = "improvement"
    CONSTRAINT = "constraint"


class Organization(Base):
    """An organization groups users, clients, and projects."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list["User"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    clients: Mapped[list["Client"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """A user belongs to an optional organization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped[Optional[Organization]] = relationship(back_populates="users")


class Client(Base):
    """A client belongs to an organization and can own projects."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped[Organization] = relationship(back_populates="clients")
    projects: Mapped[list["Project"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class Project(Base):
    """A project represents a deliverable for a client."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped[Organization] = relationship(back_populates="projects")
    client: Mapped[Optional[Client]] = relationship(back_populates="projects")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    conversation_turns: Mapped[list["ConversationTurn"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Requirement(Base):
    """A requirement captured for a project and persona."""

    __tablename__ = "requirements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[RequirementType] = mapped_column(SAEnum(RequirementType, name="requirement_type"), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cluster_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="requirements")


class ConversationTurn(Base):
    """A conversation turn captured for analysis."""

    __tablename__ = "conversation_turns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project: Mapped["Project"] = relationship(back_populates="conversation_turns")


__all__ = [
    "Base",
    "RequirementType",
    "Organization",
    "User",
    "Client",
    "Project",
    "Requirement",
    "ConversationTurn",
]
