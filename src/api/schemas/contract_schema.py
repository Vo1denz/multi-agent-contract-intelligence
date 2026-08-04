"""API request and response schemas for contract analysis."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class ContractUploadResponse(BaseModel):
    contract_id: str
    filename: str
    file_path: str
    status: str = "uploaded"


class DetectedElementSchema(BaseModel):
    label: str = ""
    bbox: list[float] = Field(default_factory=list)
    confidence: float = 0.0
    element_type: str = ""


class PageSchema(BaseModel):
    page_number: int
    page_type: str = "BODY"
    confidence: float = 0.0
    image_path: str = ""
    detected_elements: list[DetectedElementSchema] = Field(default_factory=list)


class EntitySchema(BaseModel):
    entity_type: str = ""
    value: str = ""
    span: list[int] = Field(default_factory=list)
    confidence: float = 0.0


class ClauseSchema(BaseModel):
    text: str
    section_number: Optional[str] = ""
    heading: Optional[str] = ""
    bbox: list[float] = Field(default_factory=list)
    category: str = ""
    confidence: float = 0.0
    is_cuad_category: bool = True
    precedent_text: str = ""
    semantic_deviation: float = 0.0
    risk_level: str = "LOW"
    redline_suggestion: str = ""
    is_grounded: bool = True
    entities: list[EntitySchema] = Field(default_factory=list)


class VQAIssueSchema(BaseModel):
    page_number: int = 0
    question: str = ""
    answer: str = ""
    confidence: float = 0.0
    is_complete: bool = False


class ContradictionSchema(BaseModel):
    page_number: int = 0
    handwritten_text: str = ""
    typed_text: str = ""
    severity: str = "HIGH"


class AnalysisReportResponse(BaseModel):
    contract_id: str
    status: str = "complete"
    overall_risk_score: int = 0
    risk_summary: str = ""
    execution_complete: bool = True
    critic_verified: bool = False
    pages: list[PageSchema] = Field(default_factory=list)
    clauses: list[ClauseSchema] = Field(default_factory=list)
    vqa_issues: list[VQAIssueSchema] = Field(default_factory=list)
    handwritten_contradictions: list[ContradictionSchema] = Field(default_factory=list)
    parties: list[str] = Field(default_factory=list)
    critic_notes: list[str] = Field(default_factory=list)
    audit_trail: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AgentProgressMessage(BaseModel):
    """WebSocket message for real-time agent progress."""
    agent_name: str
    status: str  # "started", "completed", "error"
    step: int  # 1-7
    total_steps: int = 7
    message: str = ""
    timestamp: str = ""
