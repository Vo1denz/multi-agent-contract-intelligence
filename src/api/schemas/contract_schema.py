"""Contract API schemas."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnalyzeContractRequest(BaseModel):
    """Request payload for contract analysis."""

    contract_id: str
    file_path: str
    enable_vqa: bool = True
    enable_playbook_rag: bool = True


class AnalyzeContractResponse(BaseModel):
    """Response payload returning risk scorecard and audit trail."""

    contract_id: str
    overall_risk_score: int
    execution_complete: bool
    critic_verified: bool
    clauses: List[Dict[str, Any]]
    audit_trail: List[str]
