from typing import Any, Literal

from pydantic import BaseModel, Field


FileType = Literal["pdf", "image"]
SourceType = Literal["text", "logs", "pdf", "image"]
Criticite = Literal["faible", "moyenne", "elevee", "critique"]


class TicketInput(BaseModel):
    """
    Entrée pour un ticket.

    Chaque ticket peut contenir :
    - du texte
    - des logs
    - un fichier PDF ou image
    """

    ticket_id: str
    ticket_text: str | None = Field(default=None)
    logs: list[dict[str, Any]] | None = Field(default=None)
    file_url: str | None = Field(default=None)
    file_type: FileType | None = Field(default=None)


class CyberTicketInput(BaseModel):
    """Entrée globale du workflow."""

    tickets: list[TicketInput]


class ParsedContent(BaseModel):
    """
    Contenu normalisé avant analyse IA.

    Exemple :
    TICKET-001 / text
    TICKET-001 / logs
    TICKET-001 / pdf
    """

    ticket_id: str
    source_type: SourceType
    content: str


class TicketAnalysis(BaseModel):
    """Analyse structurée d’un ticket."""

    ticket_id: str
    resume: str
    type_incident: str
    utilisateur: str | None = None
    application: str | None = None
    criticite: Criticite
    score_risque: int
    signaux_detectes: list[str]
    elements_suspects: list[str]
    donnees_manquantes: list[str]
    actions_recommandees: list[str]
    validation_humaine: bool
    justification: str


class BatchCyberAnalysis(BaseModel):
    """Réponse finale pour plusieurs tickets."""

    analyses: list[TicketAnalysis]
    synthese_globale: str
    tickets_prioritaires: list[str]