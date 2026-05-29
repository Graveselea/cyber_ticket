"""Models for the TPRM workflow."""

from typing import Literal

from pydantic import BaseModel, Field

from ..common.models import FileType, SourceType

RiskLevel = Literal["faible", "moyen", "eleve", "critique"]


class SupplierDocumentInput(BaseModel):
    """
    A document linked to a supplier.

    It can be:
    - free text
    - questionnaire answer
    - email content
    - PDF URL
    - image URL
    """

    document_id: str
    document_type: Literal["text", "questionnaire", "email", "pdf", "image"]
    content: str | None = Field(default=None)
    file_url: str | None = Field(default=None)
    file_type: FileType | None = Field(default=None)


class SupplierInput(BaseModel):
    """Input for one supplier."""

    supplier_id: str
    supplier_name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    documents: list[SupplierDocumentInput] = Field(default_factory=list)


class TPRMInput(BaseModel):
    """Input for the full TPRM workflow."""

    suppliers: list[SupplierInput]


class ParsedSupplierContent(BaseModel):
    """Normalized content before analysis."""

    supplier_id: str
    supplier_name: str | None = None
    source_type: SourceType
    content: str
    document_id: str | None = None


class SupplierRiskAnalysis(BaseModel):
    """Structured risk analysis for one supplier."""

    supplier_id: str
    supplier_name: str | None = None
    summary: str
    risk_level: RiskLevel
    risk_score: int
    risks_detected: list[str]
    missing_information: list[str]
    exceptions: list[str]
    recommendations: list[str]
    human_validation_required: bool
    justification: str


class BatchTPRMAnalysis(BaseModel):
    """Final output for several suppliers."""

    analyses: list[SupplierRiskAnalysis]
    global_summary: str
    priority_suppliers: list[str]
