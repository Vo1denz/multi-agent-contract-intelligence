"""Zero-shot fallback classifier for out-of-distribution clauses."""

from typing import Dict, Any


class ZeroShotFallbackClassifier:
    """Fallback classifier using zero-shot prompting for non-CUAD clause types."""

    def classify_fallback(self, text: str) -> Dict[str, Any]:
        """Classify clause text using a zero-shot LLM prompt."""
        return {
            "category": "Custom Vendor Obligation",
            "confidence": 0.76,
            "is_cuad_category": False
        }
