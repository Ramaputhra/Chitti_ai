from typing import List
from desktop.models.evidence import EvidenceCluster

class ImportanceEvaluator:
    """
    Shared evaluation logic for ranking, scoring, and summarizing evidence.
    Rule 43: Must remain provider-independent.
    """
    
    @staticmethod
    def evaluate_clusters(clusters: List[EvidenceCluster], session_duration: float):
        """
        Assigns an importance_score to each cluster based on normalized signals.
        For MVP, we use reading time / session duration as the primary signal.
        """
        if session_duration <= 0:
            session_duration = 1.0 # prevent division by zero
            
        for cluster in clusters:
            # 1. Duration Signal (0-1)
            duration_signal = min(1.0, cluster.duration / session_duration)
            
            # 2. Frequency Signal (0-1)
            # based on number of distinct sources in the cluster
            max_expected_sources = 10.0
            frequency_signal = min(1.0, len(cluster.sources) / max_expected_sources)
            
            # Combine signals (for example: 70% duration, 30% frequency)
            # This is provider-agnostic. All providers populate duration and sources.
            cluster.importance_score = round((duration_signal * 0.7) + (frequency_signal * 0.3), 3)
