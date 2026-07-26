"""Tests for end-to-end 7-agent LangGraph workflow execution."""

from src.orchestration.runner import ClauseIQRunner


def test_langgraph_pipeline_execution():
    runner = ClauseIQRunner()
    result = runner.run_analysis(
        contract_id="test_contract_01",
        file_path="sample.png"
    )
    assert result["contract_id"] == "test_contract_01"
    assert len(result["page_types"]) > 0
    assert len(result["clauses"]) > 0
    assert "overall_risk_score" in result
    assert len(result["audit_trail"]) == 7
