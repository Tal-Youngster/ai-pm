"""Entry point for running the Temporal worker."""

from __future__ import annotations

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from worker.activities import echo_activity
from worker.settings import settings
from worker.workflows import EchoWorkflow

TASK_QUEUE = "ai-pm-default"


async def main() -> None:
    """Start the Temporal worker."""

    client = await Client.connect(settings.host, namespace=settings.namespace)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[EchoWorkflow],
        activities=[echo_activity],
    )

    logging.info("Starting worker on task queue '%s'", TASK_QUEUE)
    await worker.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
