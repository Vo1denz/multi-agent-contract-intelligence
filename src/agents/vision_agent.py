from __future__ import annotations
from typing import Any
import traceback
from src.ops.logger import get_logger
from src.agents.state import ContractAnalysisState, PageInfo

logger = get_logger(__name__)

def vision_agent(state: ContractAnalysisState) -> dict[str, Any]:
    file_path = state.get("file_path")
    if not file_path:
        return {"errors": ["No file_path provided to vision_agent."]}
        
    audit_msgs = ["Vision agent started."]
    pages_out = []
    errors = []
    
    try:
        from src.vision.preprocessor import preprocess_document
        from src.vision.classifier import PageClassifier
        from src.vision.detector import LayoutDetector
        
        doc_pages = preprocess_document(file_path)
        classifier = PageClassifier()
        detector = LayoutDetector()
        
        for p in doc_pages.pages:
            classification = classifier.classify_page(p.image, p.text, p.page_number)
            elements = detector.detect_elements(p.image, p.text)
            
            page_info = PageInfo(
                page_number=p.page_number,
                page_type=classification.page_type,
                confidence=classification.confidence,
                image_path=p.file_path,
                detected_elements=[
                    {
                        "label": e.label,
                        "bbox": e.bbox,
                        "confidence": e.confidence,
                        "element_type": e.element_type
                    }
                    for e in elements
                ]
            )
            page_dict = page_info.to_dict()
            page_dict["text"] = p.text or ""
            pages_out.append(page_dict)
            
        audit_msgs.append(f"Processed {len(pages_out)} pages with vision pipeline.")
    except Exception as e:
        logger.error(f"Vision agent failed: {e}")
        errors.append(f"Vision agent error: {str(e)}")
        audit_msgs.append("Vision agent encountered an error.")
        
    return {
        "pages": pages_out,
        "audit_trail": audit_msgs,
        "errors": errors
    }
