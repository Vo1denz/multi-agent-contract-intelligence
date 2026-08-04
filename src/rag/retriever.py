from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import os
import yaml

from .embeddings import EmbeddingEngine
from .pgvector_store import VectorStore, PrecedentMatch

@dataclass
class RetrievalResult:
    precedents: List[PrecedentMatch]
    semantic_deviation: float
    is_deviant: bool
    deviation_threshold: float

class PlaybookRetriever:
    def __init__(self, vector_store: VectorStore, embedding_engine: EmbeddingEngine, playbook_rules_path: str):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        self.playbook_rules_path = playbook_rules_path
        
        if os.path.exists(playbook_rules_path):
            self.seed_from_playbook()

    def seed_from_playbook(self):
        try:
            with open(self.playbook_rules_path, 'r') as f:
                rules = yaml.safe_load(f)
                
            for rule in rules.get('rules', []):
                clause_type = rule.get('clause_type')
                text = rule.get('precedent_summary', '')
                if clause_type and text:
                    emb = self.embedding_engine.embed(text)
                    self.vector_store.insert(clause_type, text, emb)
        except Exception as e:
            pass 

    def retrieve(self, clause_text: str, clause_type: Optional[str], top_k: int = 3) -> RetrievalResult:
        query_emb = self.embedding_engine.embed(clause_text)
        
        matches = self.vector_store.search(query_emb, top_k=top_k)
        
        if clause_type:
            matches = [m for m in matches if m.clause_type == clause_type]
            
        deviation_threshold = 0.3
        
        if not matches:
            return RetrievalResult(
                precedents=[],
                semantic_deviation=1.0,
                is_deviant=True,
                deviation_threshold=deviation_threshold
            )
            
        min_dist = min(m.distance for m in matches)
        is_deviant = min_dist > deviation_threshold
        
        return RetrievalResult(
            precedents=matches,
            semantic_deviation=min_dist,
            is_deviant=is_deviant,
            deviation_threshold=deviation_threshold
        )
