"""LangGraph state schema using TypedDict with Annotated reducers."""
from __future__ import annotations
import operator
from typing import TypedDict, Annotated, Any
from dataclasses import dataclass, field, asdict

@dataclass
class ClauseItem:
    text: str
    section_number: str = ""
    heading: str = ""
    bbox: list[float] = field(default_factory=list)
    category: str = ""
    confidence: float = 0.0
    is_cuad_category: bool = True
    precedent_text: str = ""
    semantic_deviation: float = 0.0
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    redline_suggestion: str = ""
    is_grounded: bool = True
    entities: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class PageInfo:
    page_number: int
    page_type: str = "BODY"
    confidence: float = 0.0
    image_path: str = ""
    detected_elements: list[dict[str, Any]] = field(default_factory=list)
    text_blocks: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass  
class VQAIssue:
    page_number: int
    question: str
    answer: str
    confidence: float = 0.0
    is_complete: bool = False
    evidence_bbox: list[float] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class HandwrittenContradiction:
    page_number: int
    handwritten_text: str
    typed_text: str
    location_bbox: list[float] = field(default_factory=list)
    severity: str = "HIGH"
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _merge_dicts(left: dict, right: dict) -> dict:
    merged = {**left}
    for k, v in right.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = _merge_dicts(merged[k], v)
        else:
            merged[k] = v
    return merged

class ContractAnalysisState(TypedDict, total=False):
    # Input
    contract_id: str
    file_path: str
    
    # Vision outputs
    pages: Annotated[list[dict], operator.add]
    
    # Extraction outputs
    clauses: list[dict]
    raw_text: str
    parties: Annotated[list[str], operator.add]
    
    # Verification
    execution_complete: bool
    vqa_issues: Annotated[list[dict], operator.add]
    
    # Risk
    handwritten_contradictions: Annotated[list[dict], operator.add]
    overall_risk_score: int
    risk_summary: str
    
    # Critic
    critic_verified: bool
    critic_notes: Annotated[list[str], operator.add]
    
    # Audit
    audit_trail: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
