"""Tests for pgvector playbook precedents retrieval and similarity."""

from src.rag.retriever import PlaybookRetriever


def test_playbook_retriever():
    retriever = PlaybookRetriever()
    result = retriever.get_precedent_and_deviation("Limitation of Liability", "Vendor cap at 0.25x")
    assert "precedent_text" in result
    assert "semantic_deviation_score" in result
