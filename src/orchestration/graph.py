"""LangGraph 7-Agent Contract Risk Workflow Graph definition."""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..agents.state import ContractAnalysisState
from ..agents.vision_agent import document_vision_agent
from ..agents.extraction_agent import extraction_agent
from ..agents.classification_agent import classification_agent
from ..agents.verification_agent import execution_verification_agent
from ..agents.playbook_agent import playbook_comparison_agent
from ..agents.risk_agent import risk_scoring_agent
from ..agents.critic_agent import critic_agent


def build_contract_risk_graph() -> StateGraph:
    """Build and compile the 7-agent LangGraph workflow."""
    workflow = StateGraph(ContractAnalysisState)

    # Add agent nodes
    workflow.add_node("document_vision", document_vision_agent)
    workflow.add_node("extraction", extraction_agent)
    workflow.add_node("classification", classification_agent)
    workflow.add_node("verification", execution_verification_agent)
    workflow.add_node("playbook_comparison", playbook_comparison_agent)
    workflow.add_node("risk_scoring", risk_scoring_agent)
    workflow.add_node("critic", critic_agent)

    # Set workflow edges
    workflow.set_entry_point("document_vision")
    workflow.add_edge("document_vision", "extraction")
    workflow.add_edge("extraction", "classification")
    workflow.add_edge("classification", "verification")
    workflow.add_edge("verification", "playbook_comparison")
    workflow.add_edge("playbook_comparison", "risk_scoring")
    workflow.add_edge("risk_scoring", "critic")
    workflow.add_edge("critic", END)

    return workflow.compile()
