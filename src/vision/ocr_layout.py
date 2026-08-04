from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional, List, Any

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

try:
    from transformers import pipeline
    _HAS_TRANSFORMERS = True
except ImportError:
    _HAS_TRANSFORMERS = False

try:
    import pytesseract
    _HAS_PYTESSERACT = True
except ImportError:
    _HAS_PYTESSERACT = False

try:
    import pypdf
    _HAS_PYPDF = True
except ImportError:
    _HAS_PYPDF = False

@dataclass
class TextBlock:
    text: str
    bbox: List[float]
    is_handwritten: bool
    confidence: float
    block_type: str

class LayoutOCR:
    def __init__(self):
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None and _MODE == 'full' and _HAS_TRANSFORMERS:
            self._pipeline = pipeline('document-question-answering', model='impira/layoutlm-document-qa')
        return self._pipeline

    def extract(self, image: Any, file_path: Optional[str]) -> List[TextBlock]:
        blocks = []
        # Lite mode / Fallback
        if file_path and file_path.lower().endswith('.pdf') and _HAS_PYPDF:
            try:
                reader = pypdf.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        blocks.append(TextBlock(
                            text=text.strip(),
                            bbox=[0.1, 0.1, 0.8, 0.8],
                            is_handwritten=False,
                            confidence=1.0,
                            block_type="PAGE_TEXT"
                        ))
                return blocks
            except Exception:
                pass
                
        if image is not None and _HAS_PYTESSERACT:
            try:
                text = pytesseract.image_to_string(image)
                if text:
                    paragraphs = [p for p in text.split('\n\n') if p.strip()]
                    for j, p in enumerate(paragraphs):
                        blocks.append(TextBlock(
                            text=p.strip(),
                            bbox=[0.1, 0.1 + (j*0.05), 0.8, 0.05],
                            is_handwritten=False,
                            confidence=0.8,
                            block_type="PARAGRAPH"
                        ))
                return blocks
            except Exception:
                pass
                
        return blocks
