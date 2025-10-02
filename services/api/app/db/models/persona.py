"""Persona model definition."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import PersonaRole


class Persona(Base):
    """A persona participating in a project's lifecycle."""

    __tablename__ = "personas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    role: Mapped[PersonaRole] = mapped_column(SAEnum(PersonaRole, name="persona_role"), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="personas")
    user: Mapped[Optional["User"]] = relationship(back_populates="personas")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="persona", cascade="all, delete-orphan")
    conversation_turns: Mapped[list["ConversationTurn"]] = relationship(
        back_populates="persona", cascade="all, delete-orphan"
    )


__all__ = ["Persona"]
