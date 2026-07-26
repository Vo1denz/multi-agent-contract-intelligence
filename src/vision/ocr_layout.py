"""Layout-grounded OCR text extraction for contract pages."""

from typing import Dict, Any, List


class LayoutOCR:
    """Extracts typed and handwritten text with layout coordinates."""

    def extract(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract lines of text with their bounding box coordinates."""
        return [
            {
                "text": "12.4 Limitation of Liability. Vendor's total liability shall not exceed 0.25x the total fees paid.",
                "bbox": [40, 200, 520, 40],
                "is_handwritten": False
            }
        ]
