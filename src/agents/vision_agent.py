"""1. Document-Vision Agent: Multimodal layout analysis and handwritten markup localization."""

from typing import Dict, Any
from .state import ContractAnalysisState
from ..vision.classifier import PageClassifier
from ..vision.detector import LayoutDetector


def document_vision_agent(state: ContractAnalysisState) -> Dict[str, Any]:
    """Inspects scanned images, classifies page types, and detects signature blocks/redlines."""
    classifier = PageClassifier()
    detector = LayoutDetector()

    page_info = classifier.classify_page(state.file_path)
    elements = detector.detect_elements(state.file_path)

    state.page_types.append(page_info)
    state.detected_elements.extend(elements)
    state.audit_trail.append("Document-Vision Agent completed multimodal inspection.")
    return state.model_dump()
