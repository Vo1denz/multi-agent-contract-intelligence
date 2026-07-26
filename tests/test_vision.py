"""Tests for document vision classifier, object detector, and VQA."""

from src.vision.classifier import PageClassifier
from src.vision.detector import LayoutDetector


def test_page_classifier():
    classifier = PageClassifier()
    result = classifier.classify_page("sample.png")
    assert result["page_type"] == "BODY"
    assert "confidence" in result


def test_layout_detector():
    detector = LayoutDetector()
    elements = detector.detect_elements("sample.png")
    assert len(elements) == 2
    assert elements[0]["label"] == "signature_block"
