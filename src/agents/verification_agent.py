"""4. Execution-Verification Agent: Visual QA for incomplete signatures or initials."""

from typing import Dict, Any
from .state import ContractAnalysisState
from ..vision.vqa import ExecutionVQA


def execution_verification_agent(state: ContractAnalysisState) -> Dict[str, Any]:
    """Runs VQA on signature blocks and margin redlines to check execution completeness."""
    vqa = ExecutionVQA()
    check = vqa.verify_execution(state.file_path, "Are all signature blocks and margins signed?")

    if check.get("answer") == "NO_INITIAL":
        state.execution_complete = False
        state.vqa_issues.append("Missing initials on margin redline at coordinates [440, 160, 110, 32].")

    state.audit_trail.append("Execution-Verification Agent completed VQA signature check.")
    return state.model_dump()
