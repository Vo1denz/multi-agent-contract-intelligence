from __future__ import annotations
import os
from typing import List
import numpy as np

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

try:
    from sentence_transformers import SentenceTransformer
    _HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    _HAS_SENTENCE_TRANSFORMERS = False

try:
    from sklearn.feature_extraction.text import HashingVectorizer
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False

class EmbeddingEngine:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._dim = 384

    @property
    def dimension(self) -> int:
        return self._dim

    def _load_model(self):
        if self.model is None and _MODE == 'full' and _HAS_SENTENCE_TRANSFORMERS:
            self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        elif self.vectorizer is None and _HAS_SKLEARN:
            self.vectorizer = HashingVectorizer(n_features=self._dim)

    def embed(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        
        if _MODE == 'full' and self.model is not None:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
            
        if self.vectorizer is not None:
            X = self.vectorizer.transform(texts).toarray()
            norms = np.linalg.norm(X, axis=1, keepdims=True)
            norms[norms == 0] = 1
            X = X / norms
            return X.tolist()
            
        return [[0.0] * self._dim for _ in texts]
