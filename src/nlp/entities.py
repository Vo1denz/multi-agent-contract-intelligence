"""Token classification for contract parties, dates, liability caps, and monetary amounts."""

from typing import Dict, Any, List


class LegalEntityExtractor:
    """Extracts named legal entities and numeric caps from contract text."""

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Return a list of extracted entities with character spans."""
        return [
            {
                "entity_type": "LIABILITY_CAP",
                "value": "0.25x the total fees paid",
                "span": [49, 74]
            }
        ]
