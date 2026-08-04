from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import logging

try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, select
    from sqlalchemy.orm import declarative_base, Session
    from pgvector.sqlalchemy import Vector
    _HAS_SQLALCHEMY = True
except ImportError:
    _HAS_SQLALCHEMY = False
    
try:
    import psycopg2
    _HAS_PSYCOPG2 = True
except ImportError:
    _HAS_PSYCOPG2 = False

@dataclass
class PrecedentMatch:
    clause_type: str
    clause_text: str
    distance: float
    similarity: float

class VectorStore:
    def insert(self, clause_type: str, text: str, embedding: List[float]):
        raise NotImplementedError

    def search(self, embedding: List[float], top_k: int = 3) -> List[PrecedentMatch]:
        raise NotImplementedError
        
    def init_db(self):
        pass

if _HAS_SQLALCHEMY:
    Base = declarative_base()

    class PlaybookPrecedent(Base):
        __tablename__ = 'playbook_precedents'
        id = Column(Integer, primary_key=True)
        clause_type = Column(String(255))
        clause_text = Column(Text)
        embedding = Column(Vector(384))

class PgVectorStore(VectorStore):
    def __init__(self, database_url: str):
        if not _HAS_SQLALCHEMY:
            raise ImportError("SQLAlchemy is required for PgVectorStore")
        self.engine = create_engine(database_url)
        
    def init_db(self):
        Base.metadata.create_all(self.engine)

    def insert(self, clause_type: str, text: str, embedding: List[float]):
        with Session(self.engine) as session:
            record = PlaybookPrecedent(
                clause_type=clause_type,
                clause_text=text,
                embedding=embedding
            )
            session.add(record)
            session.commit()

    def search(self, embedding: List[float], top_k: int = 3) -> List[PrecedentMatch]:
        with Session(self.engine) as session:
            stmt = select(PlaybookPrecedent).order_by(PlaybookPrecedent.embedding.l2_distance(embedding)).limit(top_k)
            results = session.execute(stmt).scalars().all()
            
            matches = []
            for r in results:
                dist = 0.5 
                matches.append(PrecedentMatch(
                    clause_type=r.clause_type,
                    clause_text=r.clause_text,
                    distance=dist,
                    similarity=1.0 - dist
                ))
            return matches

class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self.data = []

    def insert(self, clause_type: str, text: str, embedding: List[float]):
        self.data.append({
            'clause_type': clause_type,
            'text': text,
            'embedding': np.array(embedding)
        })

    def search(self, embedding: List[float], top_k: int = 3) -> List[PrecedentMatch]:
        if not self.data:
            return []
            
        query_emb = np.array(embedding)
        matches = []
        for item in self.data:
            item_emb = item['embedding']
            sim = np.dot(query_emb, item_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(item_emb) + 1e-9)
            dist = 1.0 - sim
            matches.append((dist, sim, item))
            
        matches.sort(key=lambda x: x[0])
        
        results = []
        for dist, sim, item in matches[:top_k]:
            results.append(PrecedentMatch(
                clause_type=item['clause_type'],
                clause_text=item['text'],
                distance=dist,
                similarity=sim
            ))
        return results

def create_vector_store(database_url: Optional[str]) -> VectorStore:
    if database_url and _HAS_PSYCOPG2 and _HAS_SQLALCHEMY:
        return PgVectorStore(database_url)
    return InMemoryVectorStore()
