"""Analysis activity for the TPRM workflow."""

import json

import mistralai.workflows as workflows
from mistralai.workflows.plugins.mistralai import (
    ChatCompletionRequest,
    UserMessage,
    mistralai_chat_complete,
)
from pydantic import ValidationError

from ..cyber_ticket.utils import extract_json
from .models import BatchTPRMAnalysis
from .prompt import build_tprm_prompt


@workflows.activity()
async def analyse_supplier_risk(raw_content: str) -> BatchTPRMAnalysis:
    """Analyze suppliers and return a structured TPRM report."""

    print("DEBUG - start analyse_supplier_risk")
    print("DEBUG - raw_content length:", len(raw_content))

    raw_content = raw_content[:4500]
    print("DEBUG - truncated raw_content length:", len(raw_content))

    prompt = build_tprm_prompt(raw_content)

    request = ChatCompletionRequest(
        model="open-mistral-nemo",
        messages=[
            UserMessage(content=prompt),
        ],
        max_tokens=4096,
        temperature=0,
    )

    print("DEBUG - before mistralai_chat_complete")

    result = await mistralai_chat_complete(request)

    print("DEBUG - after mistralai_chat_complete")

    content = result.choices[0].message.content

    if content is None:
        raise ValueError("Empty response from Mistral.")

    print("DEBUG - model content:")
    print(content)

    try:
        json_data = extract_json(content)
        return BatchTPRMAnalysis.model_validate(json_data)
    except (json.JSONDecodeError, ValidationError, ValueError) as error:
        raise ValueError(
            f"Could not parse model response: {error}\nRaw response: {content}"
        ) from error
