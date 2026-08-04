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

EXECUTION_QUESTIONS = [
    "Is this signature block complete?",
    "Is there an initial in this margin?",
    "Is the date filled in?"
]

@dataclass
class VQAResult:
    question: str
    answer: str
    confidence: float
    evidence_bbox: Optional[List[float]]
    is_complete: bool

class ExecutionVQA:
    def __init__(self):
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None and _MODE == 'full' and _HAS_TRANSFORMERS:
            self._pipeline = pipeline('document-question-answering', model='impira/layoutlm-document-qa')
        return self._pipeline

    def verify_execution(self, image: Any, text: Optional[str], question: str) -> VQAResult:
        if _MODE == 'full' and _HAS_TRANSFORMERS and image is not None:
            pipe = self._get_pipeline()
            if pipe:
                try:
                    res = pipe(image=image, question=question)
                    if isinstance(res, list) and len(res) > 0:
                        ans = res[0]
                    else:
                        ans = res
                    return VQAResult(
                        question=question,
                        answer=ans.get('answer', ''),
                        confidence=ans.get('score', 0.0),
                        evidence_bbox=None,
                        is_complete=True if ans.get('score', 0) > 0.5 else False
                    )
                except Exception:
                    pass
        
        # Lite mode / Fallback heuristics
        q_lower = question.lower()
        if text:
            t_lower = text.lower()
            if 'signature block complete' in q_lower or 'signed' in q_lower:
                if 'by:' in t_lower and 'name:' in t_lower and 'title:' in t_lower:
                    return VQAResult(question, "Yes", 0.8, None, True)
                return VQAResult(question, "No", 0.6, None, False)
            elif 'date' in q_lower:
                if 'date: ___________' in t_lower or 'date: ______' in t_lower:
                    return VQAResult(question, "No (Date left blank)", 0.9, None, False)
                elif 'date:' in t_lower and any(char.isdigit() for char in t_lower):
                    return VQAResult(question, "Yes", 0.85, None, True)
                return VQAResult(question, "No (Date missing)", 0.8, None, False)
            elif 'initial' in q_lower:
                if 'initial' in t_lower:
                    return VQAResult(question, "Yes", 0.7, None, True)
                return VQAResult(question, "No (Missing initials)", 0.8, None, False)
        
        return VQAResult(question, "Unknown", 0.0, None, False)
