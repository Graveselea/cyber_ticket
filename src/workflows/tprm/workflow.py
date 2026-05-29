"""Main TPRM workflow."""

import mistralai.workflows as workflows

from .analysis import analyse_supplier_risk
from .models import BatchTPRMAnalysis, TPRMInput
from .parser_trpm import build_raw_content, parse_input


@workflows.workflow.define(
    name="third-party-risk-analysis",
    workflow_display_name="Third Party Risk Analysis",
    workflow_description="Analyse des risques fournisseurs / TPRM.",
)
class TPRMWorkflow:
    """Workflow for third-party risk analysis."""

    @workflows.workflow.entrypoint
    async def run(self, input: TPRMInput) -> BatchTPRMAnalysis:
        print("DEBUG - TPRM workflow started")

        parsed_contents = await parse_input(input)
        raw_content = await build_raw_content(parsed_contents)
        analysis = await analyse_supplier_risk(raw_content)

        print("DEBUG - TPRM workflow finished")

        return analysis
