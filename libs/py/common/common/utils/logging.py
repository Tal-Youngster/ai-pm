from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Any, Mapping

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: int | str = "INFO", overrides: Mapping[str, Any] | None = None) -> None:
    """Configure structured logging for services.

    This centralises logging setup so the services can opt into a consistent
    format and level. Additional configuration can be merged via *overrides*.
    """

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": _DEFAULT_FORMAT,
            }
        },
        "handlers": {
            "default": {
                "level": level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
            }
        },
        "root": {"handlers": ["default"], "level": level},
    }

    if overrides:
        config.update(overrides)

    dictConfig(config)


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger using the shared configuration."""

    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
