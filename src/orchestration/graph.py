from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from src.agents.state import ContractAnalysisState
from src.agents.vision_agent import vision_agent
from src.agents.extraction_agent import extraction_agent
from src.agents.classification_agent import classification_agent
from src.agents.verification_agent import verification_agent
from src.agents.playbook_agent import playbook_agent
from src.agents.risk_agent import risk_agent
from src.agents.critic_agent import critic_agent

def route_after_vision(state: ContractAnalysisState) -> str:
    if not state.get("pages"):
        return END
    return "extraction"

def route_after_classification(state: ContractAnalysisState) -> str:
    has_signature = any(p.get("page_type") == "SIGNATURE" for p in state.get("pages", []))
    if has_signature:
        return "verification"
    return "playbook_comparison"

def build_graph():
    builder = StateGraph(ContractAnalysisState)
    
    builder.add_node("vision", vision_agent)
    builder.add_node("extraction", extraction_agent)
    builder.add_node("classification", classification_agent)
    builder.add_node("verification", verification_agent)
    builder.add_node("playbook_comparison", playbook_agent)
    builder.add_node("risk", risk_agent)
    builder.add_node("critic", critic_agent)
    
    builder.add_edge(START, "vision")
    builder.add_conditional_edges("vision", route_after_vision)
    builder.add_edge("extraction", "classification")
    builder.add_conditional_edges("classification", route_after_classification)
    builder.add_edge("verification", "playbook_comparison")
    builder.add_edge("playbook_comparison", "risk")
    builder.add_edge("risk", "critic")
    builder.add_edge("critic", END)
    
    return builder.compile()
