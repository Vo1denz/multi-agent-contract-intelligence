"""6. Risk-Scoring Agent: Assigns risk severity levels and drafts redline suggestions."""

from typing import Dict, Any
from .state import ContractAnalysisState


def risk_scoring_agent(state: ContractAnalysisState) -> Dict[str, Any]:
    """Calculates overall risk score and creates clause-level redlines."""
    score = 0
    for clause in state.clauses:
        if clause.semantic_deviation > 0.10:
            clause.risk_level = "HIGH"
            clause.redline_suggestion = f"Align clause with playbook precedent: {clause.precedent_text}"
            score += 30
        else:
            clause.risk_level = "LOW"
            clause.redline_suggestion = "No change needed."
            score += 5

    if not state.execution_complete:
        score += 25

    state.overall_risk_score = min(score, 100)
    state.audit_trail.append(f"Risk-Scoring Agent calculated overall risk score: {state.overall_risk_score}/100.")
    return state.model_dump()
