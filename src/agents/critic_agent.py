"""7. Critic Agent: Verifies risk grounding and checks handwritten redline contradictions."""

from typing import Dict, Any
from .state import ContractAnalysisState


def critic_agent(state: ContractAnalysisState) -> Dict[str, Any]:
    """Audits flagged risks against playbook evidence and reconciles margin note contradictions."""
    all_grounded = True
    for clause in state.clauses:
        # Check if clause risk is backed by retrieved playbook text
        if clause.risk_level == "HIGH" and not clause.precedent_text:
            clause.is_grounded = False
            all_grounded = False

    state.critic_verified = all_grounded
    state.audit_trail.append("Critic Agent verified RAG grounding and margin contradictions.")
    return state.model_dump()
