import uuid
from typing import Optional
from datetime import datetime
from desktop.models.analysis import TrustAssessment
from desktop.app.trust_analyzer import TrustCandidate

class TrustValidator:
    """
    Deterministic formalizer of trust.
    Receives proposed TrustCandidates and generates persistent TrustAssessments.
    """
    
    def __init__(self, min_confidence_threshold: float = 0.8):
        self.min_confidence_threshold = min_confidence_threshold
        
    def validate_and_persist(self, candidate: TrustCandidate) -> Optional[TrustAssessment]:
        """
        Validates the candidate and creates a persistent TrustAssessment record.
        """
        # 1. Deterministic Rule: Confidence Threshold
        if candidate.confidence < self.min_confidence_threshold:
            return None
            
        # 2. Deterministic bounds checking on the score
        score = max(0.0, min(1.0, candidate.proposed_score))
            
        # 3. Create persistent TrustAssessment
        assessment = TrustAssessment(
            source_id=candidate.source_id,
            score=score,
            reason=candidate.reason,
            identity_version=candidate.identity_version,
            computed_at=datetime.now()
        )
        
        return assessment
