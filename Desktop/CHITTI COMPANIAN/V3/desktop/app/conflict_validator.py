import uuid
from typing import List
from datetime import datetime
from desktop.models.analysis import ConflictCandidate, KnowledgeConflict, ConflictStatus

class ConflictValidator:
    """
    Deterministic formalizer of conflicts.
    Receives proposed ConflictCandidates and generates persistent KnowledgeConflicts.
    """
    
    def __init__(self, min_confidence_threshold: float = 0.8):
        self.min_confidence_threshold = min_confidence_threshold
        
    def validate_and_persist(self, candidate: ConflictCandidate) -> KnowledgeConflict:
        """
        Validates the candidate and creates a persistent KnowledgeConflict record.
        """
        # 1. Deterministic Rule: Confidence Threshold
        if candidate.confidence < self.min_confidence_threshold:
            # Drop it or log it
            return None
            
        # 2. Deterministic Rule: Must have at least two records
        if len(candidate.supporting_records) < 2:
            return None
            
        # 3. Create persistent conflict
        conflict = KnowledgeConflict(
            conflict_id=str(uuid.uuid4()),
            identity_uuid=candidate.identity_uuid,
            supporting_records=candidate.supporting_records,
            conflict_type=candidate.conflict_type,
            conflict_description=candidate.reason,
            confidence=candidate.confidence,
            status=ConflictStatus.OPEN,
            created_at=datetime.now(),
            resolved_at=None,
            identity_version=candidate.identity_version
        )
        
        return conflict
