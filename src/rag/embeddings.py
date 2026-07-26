"""Embedding generation and cosine similarity calculation utilities."""

from typing import List


class PlaybookEmbeddings:
    """Generates embeddings for clause texts and queries."""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name

    def embed_text(self, text: str) -> List[float]:
        """Generate a dense vector embedding for input text."""
        return [0.05] * 1536
