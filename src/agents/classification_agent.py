"""3. Clause-Classification Agent: Fine-tuned LoRA classifier with zero-shot fallback."""

from typing import Dict, Any
from .state import ContractAnalysisState
from ..nlp.classifier import ClauseClassifier
from ..nlp.zero_shot import ZeroShotFallbackClassifier


def classification_agent(state: ContractAnalysisState) -> Dict[str, Any]:
    """Classifies each clause into standard CUAD categories or falls back to zero-shot."""
    classifier = ClauseClassifier()
    fallback = ZeroShotFallbackClassifier()

    for clause in state.clauses:
        result = classifier.classify_clause(clause.text)
        if result.get("confidence", 0.0) < 0.70:
            result = fallback.classify_fallback(clause.text)
        clause.category = result.get("category")
        clause.confidence = result.get("confidence", 0.0)

    state.audit_trail.append("Clause-Classification Agent tagged all extracted clauses.")
    return state.model_dump()
