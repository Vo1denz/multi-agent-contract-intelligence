"""Helper for running the compiled ClauseIQ LangGraph workflow."""

from typing import Dict, Any
from .graph import build_contract_risk_graph
from ..agents.state import ContractAnalysisState


class ClauseIQRunner:
    """Executes the 7-agent pipeline on a given contract document."""

    def __init__(self):
        self.graph = build_contract_risk_graph()

    def run_analysis(self, contract_id: str, file_path: str) -> Dict[str, Any]:
        """Execute the LangGraph workflow and return final state dictionary."""
        initial_state = ContractAnalysisState(
            contract_id=contract_id,
            file_path=file_path
        )
        final_state = self.graph.invoke(initial_state)
        return final_state
