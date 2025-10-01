from __future__ import annotations

from uuid import uuid4

from .logging import configure_logging, get_logger


def generate_id(prefix: str | None = None) -> str:
    """Return a sortable, url-safe identifier."""

    token = uuid4().hex
    return f"{prefix}_{token}" if prefix else token


__all__ = ["generate_id", "configure_logging", "get_logger"]
