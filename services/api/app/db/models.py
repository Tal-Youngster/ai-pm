"""SQLAlchemy models."""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for ORM models."""


class Organization(Base):
    """Placeholder organization model."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """Placeholder user model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    organization: Mapped[Optional[Organization]] = relationship(back_populates="users")


__all__ = ["Base", "Organization", "User"]
