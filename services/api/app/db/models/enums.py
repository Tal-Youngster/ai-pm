"""Enum definitions for ORM models."""

from __future__ import annotations

from enum import Enum


class RequirementType(str, Enum):
    """Requirement classification categories."""

    FEATURE = "feature"
    BUG = "bug"
    IMPROVEMENT = "improvement"
    CONSTRAINT = "constraint"


class PersonaRole(str, Enum):
    """Roles a persona can represent within a project."""

    CLIENT = "client"
    LEAD = "lead"
    DEVELOPER = "developer"
    PM_AGENT = "pm_agent"


class ProjectStatus(str, Enum):
    """Lifecycle statuses for project tracking."""

    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


__all__ = ["RequirementType", "PersonaRole", "ProjectStatus"]
