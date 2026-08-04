from __future__ import annotations
from typing import Any, Callable
from src.orchestration.graph import build_graph
from src.ops.logger import get_logger

logger = get_logger(__name__)

class ClauseIQRunner:
    def __init__(self):
        self.graph = build_graph()
        
    def run(self, contract_id: str, file_path: str) -> dict[str, Any]:
        initial_state = {
            "contract_id": contract_id,
            "file_path": file_path,
            "pages": [],
            "clauses": [],
            "raw_text": "",
            "parties": [],
            "execution_complete": False,
            "vqa_issues": [],
            "handwritten_contradictions": [],
            "overall_risk_score": 0,
            "risk_summary": "",
            "critic_verified": False,
            "critic_notes": [],
            "audit_trail": [],
            "errors": []
        }
        try:
            return self.graph.invoke(initial_state)
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            initial_state["errors"].append(str(e))
            return initial_state
            
    async def run_async(self, contract_id: str, file_path: str, progress_callback: Callable = None) -> dict[str, Any]:
        initial_state = {
            "contract_id": contract_id,
            "file_path": file_path,
            "pages": [],
            "clauses": [],
            "raw_text": "",
            "parties": [],
            "execution_complete": False,
            "vqa_issues": [],
            "handwritten_contradictions": [],
            "overall_risk_score": 0,
            "risk_summary": "",
            "critic_verified": False,
            "critic_notes": [],
            "audit_trail": [],
            "errors": []
        }
        try:
            state = initial_state
            async for step_result in self.graph.astream(initial_state):
                for node_name, node_state in step_result.items():
                    if progress_callback:
                        progress_callback(node_name, node_state)
                    state.update(node_state)
            return state
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            initial_state["errors"].append(str(e))
            return initial_state
