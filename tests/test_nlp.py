"""Tests for fine-tuned LoRA clause classifier and zero-shot fallback."""

from src.nlp.classifier import ClauseClassifier
from src.nlp.zero_shot import ZeroShotFallbackClassifier


def test_clause_classifier():
    classifier = ClauseClassifier()
    result = classifier.classify_clause("Vendor liability shall be limited...")
    assert result["category"] == "Limitation of Liability"
    assert result["is_cuad_category"] is True


def test_zero_shot_fallback():
    fallback = ZeroShotFallbackClassifier()
    result = fallback.classify_fallback("Some unusual vendor term...")
    assert "category" in result
    assert result["is_cuad_category"] is False
