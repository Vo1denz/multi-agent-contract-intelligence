from __future__ import annotations
import os
import re
from dataclasses import dataclass
from typing import List, Tuple

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

try:
    from transformers import pipeline
    _HAS_TRANSFORMERS = True
except ImportError:
    _HAS_TRANSFORMERS = False

@dataclass
class ExtractedEntity:
    entity_type: str
    value: str
    span: Tuple[int, int]
    confidence: float

class EntityExtractor:
    def __init__(self):
        self.pipeline = None

    def _load_model(self):
        if self.pipeline is None and _MODE == 'full' and _HAS_TRANSFORMERS:
            self.pipeline = pipeline('token-classification', model='dslim/bert-base-NER', aggregation_strategy='simple')

    def extract(self, text: str) -> List[ExtractedEntity]:
        results = []
        if _MODE == 'full' and _HAS_TRANSFORMERS:
            self._load_model()
            if self.pipeline:
                try:
                    preds = self.pipeline(text)
                    for p in preds:
                        results.append(ExtractedEntity(
                            entity_type=p['entity_group'],
                            value=p['word'],
                            span=(p['start'], p['end']),
                            confidence=p['score']
                        ))
                    if results:
                        return results
                except Exception:
                    pass
                    
        # Lite mode fallback
        for match in re.finditer(r'\b([A-Z][A-Za-z0-9\s,.-]+(?:Inc\.|LLC|Corp\.|Corporation|Company|Ltd\.|L\.L\.C\.|LP|L\.P\.))\b', text):
            party_name = match.group(0).strip(' ,.')
            if len(party_name) > 3 and not any(w in party_name.lower() for w in ['section', 'article', 'agreement', 'page']):
                results.append(ExtractedEntity('PARTY', party_name, match.span(), 0.9))

        for match in re.finditer(r'\b(\d{1,2}/\d{1,2}/\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})\b', text):
            results.append(ExtractedEntity('DATE', match.group(0), match.span(), 0.9))
            
        for match in re.finditer(r'\$?\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|USD|dollars))?', text, re.IGNORECASE):
            if '$' in match.group(0) or 'usd' in match.group(0).lower() or 'dollar' in match.group(0).lower():
                results.append(ExtractedEntity('MONETARY_AMOUNT', match.group(0), match.span(), 0.9))
                
        for match in re.finditer(r'\b\d+(?:\.\d+)?\s*(?:%|percent)\b', text, re.IGNORECASE):
            results.append(ExtractedEntity('PERCENTAGE', match.group(0), match.span(), 0.9))
            
        for match in re.finditer(r'\b\d+\s+(?:days|months|years)\b', text, re.IGNORECASE):
            results.append(ExtractedEntity('DURATION', match.group(0), match.span(), 0.8))
            
        return results
