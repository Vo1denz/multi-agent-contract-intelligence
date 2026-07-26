"""5. Playbook-Comparison Agent: Retrieves pgvector precedents and calculates semantic deviation."""

from typing import Dict, Any
from .state import ContractAnalysisState
from ..rag.retriever import PlaybookRetriever


def playbook_comparison_agent(state: ContractAnalysisState) -> Dict[str, Any]:
    """Retrieves playbook precedent for each clause and calculates semantic distance deviation."""
    retriever = PlaybookRetriever()

    for clause in state.clauses:
        result = retriever.get_precedent_and_deviation(clause.category or "General", clause.text)
        clause.precedent_text = result.get("precedent_text")
        clause.semantic_deviation = result.get("semantic_deviation_score", 0.0)

    state.audit_trail.append("Playbook-Comparison Agent retrieved pgvector precedents.")
    return state.model_dump()
