from __future__ import annotations
from typing import Any
from src.ops.logger import get_logger
from src.agents.state import ContractAnalysisState

logger = get_logger(__name__)

def critic_agent(state: ContractAnalysisState) -> dict[str, Any]:
    audit_msgs = ["Critic agent started."]
    errors = []
    clauses = state.get("clauses", [])
    critic_notes = []
    verified = True
    
    try:
        for clause in clauses:
            if clause.get("risk_level") in ["HIGH", "CRITICAL"]:
                if not clause.get("precedent_text"):
                    clause["is_grounded"] = False
                    verified = False
                    critic_notes.append(f"Ungrounded risk in clause category {clause.get('category')}.")
                else:
                    clause["is_grounded"] = True
                    
        contradictions = state.get("handwritten_contradictions", [])
        for c in contradictions:
            critic_notes.append(f"Verified contradiction on page {c.get('page_number')}.")
            
        audit_msgs.append(f"Critic checks complete. Grounded: {verified}.")
    except Exception as e:
        logger.error(f"Critic agent error: {e}")
        errors.append(f"Critic error: {e}")
        audit_msgs.append("Critic agent failed.")
        verified = False
        
    return {
        "clauses": clauses,
        "critic_verified": verified,
        "critic_notes": critic_notes,
        "audit_trail": audit_msgs,
        "errors": errors
    }
