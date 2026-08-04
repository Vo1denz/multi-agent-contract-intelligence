from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional, List, Dict
import math
from .classifier import CUAD_CATEGORIES, ClauseClassification

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

try:
    from transformers import pipeline
    _HAS_TRANSFORMERS = True
except ImportError:
    _HAS_TRANSFORMERS = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False

class ZeroShotClassifier:
    def __init__(self):
        self.pipeline = None

    def _load_model(self):
        if self.pipeline is None and _MODE == 'full' and _HAS_TRANSFORMERS:
            self.pipeline = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

    def classify(self, text: str, candidate_labels: Optional[List[str]] = None) -> ClauseClassification:
        labels = candidate_labels or CUAD_CATEGORIES
        
        if _MODE == 'full' and _HAS_TRANSFORMERS:
            self._load_model()
            if self.pipeline:
                try:
                    res = self.pipeline(text, labels)
                    return ClauseClassification(
                        category=res['labels'][0],
                        confidence=res['scores'][0],
                        is_cuad_category=res['labels'][0] in CUAD_CATEGORIES,
                        all_scores=dict(zip(res['labels'], res['scores']))
                    )
                except Exception:
                    pass
                    
        # Lite mode fallback
        if _HAS_SKLEARN:
            vectorizer = TfidfVectorizer()
            try:
                tfidf_matrix = vectorizer.fit_transform([text] + labels)
                sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                best_idx = sim_scores.argmax()
                best_score = sim_scores[best_idx]
                return ClauseClassification(
                    category=labels[best_idx],
                    confidence=float(best_score),
                    is_cuad_category=labels[best_idx] in CUAD_CATEGORIES,
                    all_scores={labels[i]: float(sim_scores[i]) for i in range(len(labels))}
                )
            except Exception:
                pass
                
        # Dumb fallback
        return ClauseClassification(labels[0], 0.0, labels[0] in CUAD_CATEGORIES, None)
