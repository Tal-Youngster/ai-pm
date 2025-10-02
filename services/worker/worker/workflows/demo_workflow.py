"""Demo workflow that echoes a message via an activity."""

from __future__ import annotations

from datetime import timedelta

from opentelemetry import trace
from temporalio import workflow

from worker.activities.demo_activity import echo_activity

tracer = trace.get_tracer(__name__)


@workflow.defn
class EchoWorkflow:
    """A simple workflow that echoes messages."""

    @workflow.run
    async def run(self, message: str) -> str:
        """Execute the workflow and return the echoed message."""

        with tracer.start_as_current_span("EchoWorkflow.run") as span:
            span.set_attribute("workflow.input.message", message)

            result = await workflow.execute_activity(
                echo_activity,
                message,
                schedule_to_close_timeout=timedelta(seconds=10),
            )

            span.set_attribute("workflow.result.message", result)
            return result
