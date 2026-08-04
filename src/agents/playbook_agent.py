from __future__ import annotations
from typing import Any
from src.ops.logger import get_logger
from src.agents.state import ContractAnalysisState
from config.settings import settings

logger = get_logger(__name__)

def playbook_agent(state: ContractAnalysisState) -> dict[str, Any]:
    audit_msgs = ["Playbook agent started."]
    errors = []
    clauses = state.get("clauses", [])
    handwritten_contradictions = []
    
    try:
        from src.rag.retriever import PlaybookRetriever
        from src.rag.embeddings import EmbeddingEngine
        from src.rag.pgvector_store import create_vector_store
        
        store = create_vector_store(settings.database_url)
        embedder = EmbeddingEngine()
        retriever = PlaybookRetriever(store, embedder, "config/playbook_rules.yaml")
        
        for clause in clauses:
            txt = clause.get("text", "").lower()
            cat = clause.get("category", "")
            if cat:
                res = retriever.retrieve(clause.get("text", ""), cat, top_k=1)
                if res and hasattr(res, "precedents") and res.precedents:
                    p0 = res.precedents[0]
                    clause["precedent_text"] = p0.clause_text if hasattr(p0, "clause_text") else str(p0)
                    clause["semantic_deviation"] = getattr(res, "semantic_deviation", 0.0)
                else:
                    clause["semantic_deviation"] = getattr(res, "semantic_deviation", 0.0)

            # Rule-based semantic deviation & precedent matching for lite mode
            if "uncapped liability" in txt or "unlimited liability" in txt or "notwithstanding anything to the contrary" in txt:
                clause["semantic_deviation"] = max(clause.get("semantic_deviation", 0.0), 0.85)
                clause["precedent_text"] = "Liability must be capped at 1x to 2x total fees paid in the preceding 12 months."
            elif "indemnify, defend, and hold harmless" in txt and not "third-party ip" in txt:
                clause["semantic_deviation"] = max(clause.get("semantic_deviation", 0.0), 0.70)
                clause["precedent_text"] = "Mutual indemnification limited to third-party intellectual property claims."
            elif "twenty-four (24) months" in txt or "broad non-compete" in txt:
                clause["semantic_deviation"] = max(clause.get("semantic_deviation", 0.0), 0.75)
                clause["precedent_text"] = "Non-compete clauses should not exceed 12 months."
            elif "perpetual, irrevocable, worldwide" in txt:
                clause["semantic_deviation"] = max(clause.get("semantic_deviation", 0.0), 0.65)
                clause["precedent_text"] = "Licenses should be scoped to project deliverables rather than broad pre-existing IP."
                
        audit_msgs.append("Playbook comparison finished.")
    except Exception as e:
        logger.error(f"Playbook agent error: {e}")
        errors.append(f"Playbook error: {e}")
        audit_msgs.append("Playbook agent failed.")
        
    return {
        "clauses": clauses,
        "handwritten_contradictions": handwritten_contradictions,
        "audit_trail": audit_msgs,
        "errors": errors
    }
