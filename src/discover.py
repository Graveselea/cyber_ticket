"""Discover and run local Mistral workflows."""

import mistralai.workflows as workflows

from src.workflows.cyber_ticket.workflow import CyberTicketWorkflow
from src.workflows.tprm.workflow import TPRMWorkflow


async def main() -> None:
    """Start the local worker with all available workflows."""

    workflows_to_run = [
        CyberTicketWorkflow,
        TPRMWorkflow,
    ]

    print(
        "Discovered workflow(s): "
        + ", ".join(workflow.__name__ for workflow in workflows_to_run)
    )

    await workflows.run_worker(workflows_to_run)
