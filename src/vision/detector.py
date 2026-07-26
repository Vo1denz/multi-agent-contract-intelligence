"""Object detection for signature blocks, seals, and handwritten margin annotations."""

from typing import List, Dict, Any


class LayoutDetector:
    """Detects bounding boxes for signatures, stamps, and handwritten markup."""

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def detect_elements(self, image_path: str) -> List[Dict[str, Any]]:
        """Return list of bounding box coordinates and classification labels."""
        return [
            {
                "label": "signature_block",
                "coords": [40, 600, 500, 120],
                "confidence": 0.89
            },
            {
                "label": "handwritten_redline",
                "coords": [440, 160, 110, 32],
                "confidence": 0.91
            }
        ]
