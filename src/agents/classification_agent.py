from __future__ import annotations
from typing import Any
from src.ops.logger import get_logger
from src.agents.state import ContractAnalysisState
from config.settings import settings

logger = get_logger(__name__)

def classification_agent(state: ContractAnalysisState) -> dict[str, Any]:
    audit_msgs = ["Classification agent started."]
    errors = []
    clauses = state.get("clauses", [])
    
    if not clauses:
        audit_msgs.append("No clauses to classify.")
        return {"audit_trail": audit_msgs}
        
    try:
        from src.nlp.classifier import ClauseClassifier
        from src.nlp.zero_shot import ZeroShotClassifier
        
        fine_tuned = ClauseClassifier()
        zero_shot = ZeroShotClassifier()
        threshold = settings.classification_confidence_threshold
        
        for clause in clauses:
            res = fine_tuned.classify(clause.get("text", ""))
            if res.confidence < threshold:
                res = zero_shot.classify(clause.get("text", ""))
                
            clause["category"] = res.category
            clause["confidence"] = res.confidence
            clause["is_cuad_category"] = res.is_cuad_category
            
        audit_msgs.append(f"Classified {len(clauses)} clauses.")
    except Exception as e:
        logger.error(f"Classification agent error: {e}")
        errors.append(f"Classification agent error: {e}")
        audit_msgs.append("Classification agent failed.")
        
    return {
        "clauses": clauses,
        "audit_trail": audit_msgs,
        "errors": errors
    }
