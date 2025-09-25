"""Demo workflow that echoes a message via an activity."""

from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

from worker.activities.demo_activity import echo_activity


@workflow.defn
class EchoWorkflow:
    """A simple workflow that echoes messages."""

    @workflow.run
    async def run(self, message: str) -> str:
        """Execute the workflow and return the echoed message."""

        return await workflow.execute_activity(
            echo_activity,
            message,
            schedule_to_close_timeout=timedelta(seconds=10),
        )
