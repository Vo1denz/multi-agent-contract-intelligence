from __future__ import annotations
from typing import Any
from src.ops.logger import get_logger
from src.agents.state import ContractAnalysisState, ClauseItem

logger = get_logger(__name__)

def extraction_agent(state: ContractAnalysisState) -> dict[str, Any]:
    audit_msgs = ["Extraction agent started."]
    errors = []
    clauses_out = []
    raw_text = ""
    parties = []
    
    try:
        from src.vision.ocr_layout import LayoutOCR
        from src.nlp.clause_splitter import split_into_clauses
        from src.nlp.entities import EntityExtractor
        
        ocr = LayoutOCR()
        extractor = EntityExtractor()
        
        pages = state.get("pages", [])
        file_path = state.get("file_path", "")
        
        if file_path and file_path.lower().endswith('.pdf'):
            text_blocks = ocr.extract(None, file_path)
            for block in text_blocks:
                raw_text += block.text + "\n"
        else:
            for p in pages:
                if p.get("text"):
                    raw_text += p["text"] + "\n"
                elif p.get("image_path"):
                    text_blocks = ocr.extract(None, p["image_path"])
                    for block in text_blocks:
                        raw_text += block.text + "\n"
                    
        segments = split_into_clauses(raw_text)
        
        for seg in segments:
            entities = extractor.extract(seg.text)
            clause_entities = []
            for e in entities:
                clause_entities.append({
                    "entity_type": e.entity_type,
                    "value": e.value,
                    "span": e.span,
                    "confidence": e.confidence
                })
                if e.entity_type.upper() == "PARTY":
                    parties.append(e.value)
                    
            clause = ClauseItem(
                text=seg.text,
                section_number=seg.section_number,
                heading=seg.heading,
                entities=clause_entities
            )
            clauses_out.append(clause.to_dict())
            
        audit_msgs.append(f"Extracted {len(clauses_out)} clauses and {len(set(parties))} parties.")
    except Exception as e:
        logger.error(f"Extraction agent error: {e}")
        errors.append(f"Extraction agent error: {e}")
        audit_msgs.append("Extraction agent failed.")
        
    return {
        "clauses": clauses_out,
        "raw_text": raw_text,
        "parties": list(set(parties)),
        "audit_trail": audit_msgs,
        "errors": errors
    }
