import mistralai.workflows as workflows

from .analysis import analyse_ticket
from .models import BatchCyberAnalysis, CyberTicketInput
from .parser_cyber import build_raw_content, parse_input_cyber


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

        parsed_contents = await parse_input_cyber(input)
        raw_content = await build_raw_content(parsed_contents)
        analysis = await analyse_ticket(raw_content)

        print("DEBUG - workflow finished")

        return analysis
