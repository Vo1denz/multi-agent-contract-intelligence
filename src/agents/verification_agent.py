from __future__ import annotations
from typing import Any
from src.ops.logger import get_logger
from src.agents.state import ContractAnalysisState, VQAIssue

logger = get_logger(__name__)

def verification_agent(state: ContractAnalysisState) -> dict[str, Any]:
    audit_msgs = ["Verification agent started."]
    errors = []
    vqa_issues = []
    execution_complete = True
    
    try:
        from src.vision.vqa import ExecutionVQA
        vqa = ExecutionVQA()
        
        pages = state.get("pages", [])
        sig_pages = [p for p in pages if p.get("page_type") == "SIGNATURE"]
        
        if not sig_pages:
            audit_msgs.append("No signature pages found. Assuming incomplete execution.")
            execution_complete = False
        else:
            questions = [
                "Is this signature block signed?",
                "Is there a date next to the signature?",
                "Are there initials in the margin?"
            ]
            
            for p in sig_pages:
                image_path = p.get("image_path")
                page_num = p.get("page_number", 0)
                
                for q in questions:
                    res = vqa.verify_execution(image_path, p.get("text", ""), q)
                    if not res.is_complete:
                        execution_complete = False
                        issue = VQAIssue(
                            page_number=page_num,
                            question=q,
                            answer=res.answer,
                            confidence=res.confidence,
                            is_complete=res.is_complete,
                            evidence_bbox=res.evidence_bbox
                        )
                        vqa_issues.append(issue.to_dict())
                        
        audit_msgs.append(f"Execution verification complete. Status: {execution_complete}.")
    except Exception as e:
        logger.error(f"Verification agent error: {e}")
        errors.append(f"Verification agent error: {e}")
        audit_msgs.append("Verification agent failed.")
        execution_complete = False
        
    return {
        "execution_complete": execution_complete,
        "vqa_issues": vqa_issues,
        "audit_trail": audit_msgs,
        "errors": errors
    }
