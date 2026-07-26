"""2. Extraction Agent: Pulls clause text and metadata grounded in vision layout coordinates."""

from typing import Dict, Any
from .state import ContractAnalysisState, ClauseItem
from ..vision.ocr_layout import LayoutOCR


def extraction_agent(state: ContractAnalysisState) -> Dict[str, Any]:
    """Extracts clauses from document pages using layout coordinates."""
    ocr = LayoutOCR()
    extracted_lines = ocr.extract(state.file_path)

    for line in extracted_lines:
        state.clauses.append(
            ClauseItem(
                text=line.get("text", ""),
                bbox=line.get("bbox")
            )
        )

    state.audit_trail.append("Extraction Agent completed layout-grounded text extraction.")
    return state.model_dump()
