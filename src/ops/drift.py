from __future__ import annotations
from typing import Optional
from dataclasses import dataclass
import numpy as np
from src.ops.logger import get_logger

logger = get_logger(__name__)

@dataclass
class DriftResult:
    drift_detected: bool
    mean_distance: float
    threshold: float
    sample_size: int

class DriftMonitor:
    def __init__(self, baseline_embeddings: Optional[list[list[float]]] = None):
        self.baseline_embeddings = []
        if baseline_embeddings:
            self.baseline_embeddings.extend(baseline_embeddings)
            
    def add_baseline(self, embeddings: list[list[float]]):
        self.baseline_embeddings.extend(embeddings)
        
    def check_drift(self, incoming_embeddings: list[list[float]], threshold: float = 0.25) -> DriftResult:
        if not self.baseline_embeddings or not incoming_embeddings:
            return DriftResult(False, 0.0, threshold, len(incoming_embeddings))
            
        try:
            base_arr = np.array(self.baseline_embeddings)
            inc_arr = np.array(incoming_embeddings)
            
            base_centroid = np.mean(base_arr, axis=0)
            inc_centroid = np.mean(inc_arr, axis=0)
            
            cos_sim = np.dot(base_centroid, inc_centroid) / (np.linalg.norm(base_centroid) * np.linalg.norm(inc_centroid))
            mean_dist = 1.0 - cos_sim
            
            return DriftResult(
                drift_detected=(mean_dist > threshold),
                mean_distance=float(mean_dist),
                threshold=threshold,
                sample_size=len(incoming_embeddings)
            )
        except Exception as e:
            logger.error(f"Error checking drift: {e}")
            return DriftResult(False, 0.0, threshold, len(incoming_embeddings))
