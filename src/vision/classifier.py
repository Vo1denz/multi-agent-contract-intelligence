from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional, Any

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

try:
    from transformers import pipeline
    _HAS_TRANSFORMERS = True
except ImportError:
    _HAS_TRANSFORMERS = False

@dataclass
class PageClassification:
    page_type: str
    confidence: float
    reasoning: str

class PageClassifier:
    def __init__(self):
        self._pipeline: Optional[Any] = None

    def _get_pipeline(self):
        if self._pipeline is None and _MODE == 'full' and _HAS_TRANSFORMERS:
            self._pipeline = pipeline('image-classification', model='microsoft/dit-base-finetuned-rvlcdip')
        return self._pipeline

    def classify_page(self, image: Any, text: Optional[str], page_number: int = 1) -> PageClassification:
        if _MODE == 'full' and _HAS_TRANSFORMERS and image is not None:
            pipe = self._get_pipeline()
            if pipe:
                try:
                    results = pipe(image)
                    best = results[0]
                    label = best['label'].lower()
                    mapped = "BODY"
                    if "letter" in label or "memo" in label:
                        mapped = "COVER"
                    elif "form" in label:
                        mapped = "SIGNATURE"
                    
                    return PageClassification(
                        page_type=mapped,
                        confidence=best['score'],
                        reasoning=f"Model predicted {best['label']} with {best['score']:.2f} confidence"
                    )
                except Exception:
                    pass

        # Lite mode / Fallback heuristics
        if text:
            text_lower = text.lower()
            if any(k in text_lower for k in ['signature page', 'in witness whereof', 'by: _______', 'signed by', 'authorized signature']):
                return PageClassification('SIGNATURE', 0.9, "Found signature page keywords")
            elif any(k in text_lower for k in ['exhibit a', 'exhibit b', 'statement of work', 'schedule 1', 'appendix a']):
                return PageClassification('EXHIBIT', 0.85, "Found exhibit keywords")
            elif page_number == 1 and ('agreement' in text_lower or 'contract' in text_lower):
                return PageClassification('COVER', 0.8, "Found cover page keywords on page 1")
        
        return PageClassification('BODY', 0.5, "Defaulting to body page")

