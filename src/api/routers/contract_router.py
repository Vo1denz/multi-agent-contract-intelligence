"""Contract upload and analysis endpoint router."""

from fastapi import APIRouter
from ..schemas.contract_schema import AnalyzeContractRequest, AnalyzeContractResponse
from ...orchestration.runner import ClauseIQRunner

router = APIRouter(prefix="/api/v1/contracts", tags=["Contracts"])


@router.post("/analyze", response_model=AnalyzeContractResponse)
async def analyze_contract(request: AnalyzeContractRequest):
    """Run the 7-agent LangGraph workflow on the requested contract."""
    runner = ClauseIQRunner()
    result = runner.run_analysis(
        contract_id=request.contract_id,
        file_path=request.file_path
    )

    return AnalyzeContractResponse(
        contract_id=result.get("contract_id", request.contract_id),
        overall_risk_score=result.get("overall_risk_score", 0),
        execution_complete=result.get("execution_complete", True),
        critic_verified=result.get("critic_verified", False),
        clauses=[c if isinstance(c, dict) else c.model_dump() for c in result.get("clauses", [])],
        audit_trail=result.get("audit_trail", [])
    )
