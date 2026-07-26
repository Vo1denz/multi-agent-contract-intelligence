"""Playbook precedent retriever combining pgvector search and semantic deviation scores."""

from typing import List, Dict, Any
from .pgvector_store import PgVectorStore
from .embeddings import PlaybookEmbeddings


class PlaybookRetriever:
    """Retrieves acceptable playbook precedents for a classified clause."""

    def __init__(self):
        self.store = PgVectorStore()
        self.embedder = PlaybookEmbeddings()

    def get_precedent_and_deviation(self, category: str, clause_text: str) -> Dict[str, Any]:
        """Return closest playbook precedent and compute embedding deviation distance."""
        embedding = self.embedder.embed_text(clause_text)
        matches = self.store.similarity_search(embedding, top_k=1)
        match = matches[0] if matches else {}
        return {
            "precedent_text": match.get("text", "No precedent found"),
            "semantic_deviation_score": match.get("distance", 0.0),
            "is_deviant": match.get("distance", 0.0) > 0.10
        }
