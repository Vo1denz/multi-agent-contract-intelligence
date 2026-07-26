"""Shared LangGraph state schema definitions."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ClauseItem(BaseModel):
    """Represents a single extracted clause and its risk assessment."""

    text: str
    bbox: Optional[List[float]] = None
    category: Optional[str] = None
    confidence: float = 0.0
    precedent_text: Optional[str] = None
    semantic_deviation: float = 0.0
    risk_level: str = "LOW"
    redline_suggestion: Optional[str] = None
    is_grounded: bool = True


class ContractAnalysisState(BaseModel):
    """LangGraph state passed across all 7 agents in the workflow."""

    contract_id: str
    file_path: str
    page_types: List[Dict[str, Any]] = Field(default_factory=list)
    detected_elements: List[Dict[str, Any]] = Field(default_factory=list)
    execution_complete: bool = True
    vqa_issues: List[str] = Field(default_factory=list)
    clauses: List[ClauseItem] = Field(default_factory=list)
    overall_risk_score: int = 0
    critic_verified: bool = False
    audit_trail: List[str] = Field(default_factory=list)
