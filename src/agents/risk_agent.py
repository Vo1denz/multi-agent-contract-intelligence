from __future__ import annotations
from typing import Any
import yaml
from src.ops.logger import get_logger
from src.agents.state import ContractAnalysisState

logger = get_logger(__name__)

def risk_agent(state: ContractAnalysisState) -> dict[str, Any]:
    audit_msgs = ["Risk agent started."]
    errors = []
    clauses = state.get("clauses", [])
    overall_score = 0
    risk_summary = ""
    
    try:
        criticalities = {
            "Cap On Liability": 45,
            "Limitation of Liability": 45,
            "Indemnification": 40,
            "Non-Compete": 35,
            "Ip Ownership Assignment": 30,
            "Confidentiality": 25,
            "Termination For Convenience": 25,
            "Governing Law": 15,
            "Insurance": 15,
            "Audit Rights": 20,
            "Warranty Duration": 15,
        }
        try:
            with open("config/playbook_rules.yaml", "r") as f:
                rules = yaml.safe_load(f)
                if rules and "rules" in rules:
                    for r in rules["rules"]:
                        ctype = r.get("clause_type")
                        crit = r.get("criticality", "MEDIUM")
                        score_map = {"CRITICAL": 50, "HIGH": 40, "MEDIUM": 25, "LOW": 15}
                        if ctype:
                            criticalities[ctype] = score_map.get(crit, 25)
        except Exception:
            pass
            
        total_risk = 0
        execution_penalty = 25 if not state.get("execution_complete", True) else 0
        
        for clause in clauses:
            dev_score = min(55, clause.get("semantic_deviation", 0.0) * 100)
            cat = clause.get("category", "")
            crit_score = criticalities.get(cat, criticalities.get(cat.upper(), 15))
            
            clause_score = dev_score + crit_score
            if clause_score > 80:
                clause["risk_level"] = "CRITICAL"
                clause["redline_suggestion"] = "Remove or heavily modify this clause to meet standards."
            elif clause_score > 60:
                clause["risk_level"] = "HIGH"
                clause["redline_suggestion"] = "Review and revise high-risk terms."
            elif clause_score > 35:
                clause["risk_level"] = "MEDIUM"
                clause["redline_suggestion"] = "Standard review recommended."
            else:
                clause["risk_level"] = "LOW"
                
            total_risk += clause_score
            
        overall_score = int(min(100, (total_risk / max(1, len(clauses))) + execution_penalty)) if clauses else 0
        risk_summary = f"Overall Risk Score: {overall_score}/100."
        
        audit_msgs.append("Risk scoring complete.")
    except Exception as e:
        logger.error(f"Risk agent error: {e}")
        errors.append(f"Risk error: {e}")
        audit_msgs.append("Risk agent failed.")
        
    return {
        "clauses": clauses,
        "overall_risk_score": overall_score,
        "risk_summary": risk_summary,
        "audit_trail": audit_msgs,
        "errors": errors
    }
