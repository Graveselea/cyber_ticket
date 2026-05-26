import json
from typing import Any
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Vérifie rapidement si une URL semble valide."""
    result = urlparse(url)
    return bool(result.scheme and result.netloc)


def logs_to_text(logs: list[dict[str, Any]]) -> str:
    """Transforme des logs JSON en texte lisible."""
    lines: list[str] = []

    for log in logs:
        line = " | ".join(f"{key}: {value}" for key, value in log.items())
        lines.append(line)

    return "\n".join(lines)


def extract_json(text: str) -> dict[str, Any]:
    """
    Extrait un JSON depuis une réponse modèle.

    Utile si le modèle ajoute par erreur ```json autour.
    """

    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(f"Aucun JSON trouvé dans la réponse : {text}")

    return json.loads(cleaned[start:end + 1])