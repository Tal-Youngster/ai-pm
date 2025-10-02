"""Demo activity implementations."""

from __future__ import annotations

from temporalio import activity


@activity.defn
async def echo_activity(message: str) -> str:
    """Return the provided message."""

    return message
