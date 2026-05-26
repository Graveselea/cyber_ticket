import mistralai.workflows as workflows

from .cyber_analysis import analyse_ticket
from .cyber_models import BatchCyberAnalysis, CyberTicketInput
from .cyber_parser import build_raw_content, parse_input


@workflows.workflow.define(
    name="cyber-ticket-analysis",
    workflow_display_name="Cyber Ticket Analysis",
    workflow_description=(
        "Analyse des tickets cyber avec texte, logs, PDF ou image."
    ),
)
class CyberTicketWorkflow:
    """Workflow principal."""

    @workflows.workflow.entrypoint
    async def run(self, input: CyberTicketInput) -> BatchCyberAnalysis:
        print("DEBUG - workflow started")

        parsed_contents = await parse_input(input)
        raw_content = await build_raw_content(parsed_contents)
        analysis = await analyse_ticket(raw_content)

        print("DEBUG - workflow finished")

        return analysis