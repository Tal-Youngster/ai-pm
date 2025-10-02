"""Tests for the demo workflow."""

from __future__ import annotations

import asyncio

from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from worker.activities import echo_activity
from worker.workflows import EchoWorkflow


async def _run_demo_workflow() -> None:
    env = await WorkflowEnvironment.start_time_skipping()
    async with env:
        async with Worker(
            env.client,
            task_queue="ai-pm-default",
            workflows=[EchoWorkflow],
            activities=[echo_activity],
        ):
            result = await env.client.execute_workflow(
                EchoWorkflow.run,
                "hello world",
                id="demo-workflow",
                task_queue="ai-pm-default",
            )

        assert result == "hello world"

def test_demo_workflow() -> None:
    asyncio.run(_run_demo_workflow())

