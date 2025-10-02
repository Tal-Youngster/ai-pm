"""Declarative base for ORM models."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative class for ORM models."""


__all__ = ["Base"]
