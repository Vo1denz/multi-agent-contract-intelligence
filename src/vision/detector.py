from __future__ import annotations
import os
import re
from dataclasses import dataclass
from typing import Optional, List, Any

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

try:
    from transformers import pipeline
    _HAS_TRANSFORMERS = True
except ImportError:
    _HAS_TRANSFORMERS = False

@dataclass
class DetectedElement:
    label: str
    bbox: List[float]
    confidence: float
    element_type: str

class LayoutDetector:
    def __init__(self):
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None and _MODE == 'full' and _HAS_TRANSFORMERS:
            self._pipeline = pipeline('object-detection', model='facebook/detr-resnet-50')
        return self._pipeline

    def detect_elements(self, image: Any, text: Optional[str]) -> List[DetectedElement]:
        results = []
        if _MODE == 'full' and _HAS_TRANSFORMERS and image is not None:
            pipe = self._get_pipeline()
            if pipe:
                try:
                    preds = pipe(image)
                    for p in preds:
                        bbox = [p['box']['xmin']/1000.0, p['box']['ymin']/1000.0, 
                                (p['box']['xmax']-p['box']['xmin'])/1000.0, (p['box']['ymax']-p['box']['ymin'])/1000.0]
                        results.append(DetectedElement(
                            label=p['label'],
                            bbox=bbox,
                            confidence=p['score'],
                            element_type="SIGNATURE_BLOCK" if "person" in p['label'] else "UNKNOWN"
                        ))
                    if results:
                        return results
                except Exception:
                    pass
        
        # Lite mode / Fallback heuristics
        if text:
            text_lower = text.lower()
            if re.search(r'(signature:|sign:|by:|authorized)', text_lower):
                results.append(DetectedElement(
                    label='signature_area',
                    bbox=[0.1, 0.8, 0.4, 0.1],
                    confidence=0.7,
                    element_type='SIGNATURE_BLOCK'
                ))
            if re.search(r'(initial|strike|margin)', text_lower):
                results.append(DetectedElement(
                    label='handwritten_annotation',
                    bbox=[0.8, 0.1, 0.1, 0.8],
                    confidence=0.6,
                    element_type='HANDWRITTEN_REDLINE'
                ))
                
        return results
