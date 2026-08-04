from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional, List, Dict

_MODE = os.getenv('CLAUSEIQ_MODE', 'lite')

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    _HAS_TRANSFORMERS = True
except ImportError:
    _HAS_TRANSFORMERS = False

CUAD_CATEGORIES = [
    "Document Name", "Parties", "Agreement Date", "Effective Date", "Expiration Date",
    "Renewal Term", "Notice Period To Terminate Renewal", "Governing Law",
    "Most Favored Nation", "Non-Compete", "Exclusivity", "No-Solicit Of Customers",
    "Competitive Restriction Exception", "No-Solicit Of Employees",
    "Non-Disparagement", "Termination For Convenience", "Rofr/Rofo/Rofn",
    "Change Of Control", "Anti-Assignment", "Revenue/Profit Sharing",
    "Price Restriction", "Volume Restriction", "Ip Ownership Assignment",
    "Joint Ip Ownership", "License Grant", "Non-Transferable License",
    "Affiliate License-Licensor", "Affiliate License-Licensee", "Unlimited/All-You-Can-Eat-License",
    "Irrevocable Or Perpetual License", "Source Code Escrow", "Post-Termination Services",
    "Audit Rights", "Uncapped Liability", "Cap On Liability", "Liquidated Damages",
    "Warranty Duration", "Insurance", "Covenant Not To Sue", "Third Party Beneficiary"
]

@dataclass
class ClauseClassification:
    category: str
    confidence: float
    is_cuad_category: bool
    all_scores: Optional[Dict[str, float]]

class ClauseClassifier:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.keyword_mapping = {
            'liability': 'Cap On Liability',
            'indemnif': 'Indemnification',
            'terminat': 'Termination For Convenience',
            'confidential': 'Confidentiality',
            'governing law': 'Governing Law',
            'non-compete': 'Non-Compete',
            'assignment': 'Anti-Assignment',
            'warranty': 'Warranty Duration',
            'insurance': 'Insurance',
            'audit': 'Audit Rights',
            'license': 'License Grant',
            'intellectual property': 'Ip Ownership Assignment',
            'force majeure': 'Force Majeure',
            'severability': 'Severability',
            'notices': 'Notices',
            'jurisdiction': 'Governing Law'
        }

    def _load_model(self):
        if self.model is None and _MODE == 'full' and _HAS_TRANSFORMERS:
            model_name = "distilbert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def classify(self, text: str) -> ClauseClassification:
        return self.classify_batch([text])[0]

    def classify_batch(self, texts: List[str]) -> List[ClauseClassification]:
        results = []
        if _MODE == 'full' and _HAS_TRANSFORMERS:
            self._load_model()
            if self.model and self.tokenizer:
                try:
                    inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    
                    for p in probs:
                        score, idx = torch.max(p, dim=0)
                        results.append(ClauseClassification(
                            category=CUAD_CATEGORIES[idx.item() % len(CUAD_CATEGORIES)],
                            confidence=score.item(),
                            is_cuad_category=True,
                            all_scores=None
                        ))
                    return results
                except Exception:
                    pass
        
        # Lite mode fallback
        for text in texts:
            text_lower = text.lower()
            scores = {}
            for kw, cat in self.keyword_mapping.items():
                count = text_lower.count(kw)
                if count > 0:
                    scores[cat] = scores.get(cat, 0) + count
            
            if scores:
                best_cat = max(scores, key=scores.get)
                total = sum(scores.values())
                results.append(ClauseClassification(
                    category=best_cat,
                    confidence=scores[best_cat]/total,
                    is_cuad_category=best_cat in CUAD_CATEGORIES,
                    all_scores={k: v/total for k,v in scores.items()}
                ))
            else:
                results.append(ClauseClassification("Other", 1.0, False, {}))
                
        return results
