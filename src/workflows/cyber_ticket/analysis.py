import json

import mistralai.workflows as workflows
from mistralai.workflows.plugins.mistralai import (
    ChatCompletionRequest,
    UserMessage,
    mistralai_chat_complete,
)
from pydantic import ValidationError

from .models import BatchCyberAnalysis
from .prompt import build_analysis_prompt
from .utils import extract_json


@workflows.activity()
async def analyse_ticket(raw_content: str) -> BatchCyberAnalysis:
    """
    Envoie le contenu normalisé à Mistral.

    Retourne une analyse structurée en JSON.
    """

    print("DEBUG - start analyse_ticket")
    print("DEBUG - raw_content length:", len(raw_content))

    raw_content = raw_content[:4500]
    print("DEBUG - truncated raw_content length:", len(raw_content))

    prompt = build_analysis_prompt(raw_content)

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
        raise ValueError("Réponse vide du modèle Mistral.")

    print("DEBUG - model content:")
    print(content)

    try:
        json_data = extract_json(content)
        return BatchCyberAnalysis.model_validate(json_data)
    except (json.JSONDecodeError, ValidationError, ValueError) as error:
        raise ValueError(
            f"Impossible de parser la réponse du modèle : {error}\n"
            f"Réponse brute : {content}"
        ) from error
