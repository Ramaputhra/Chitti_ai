import difflib
from typing import List, Optional
from desktop.models.memory import KnowledgeRecord, KnowledgeRecordStatus
from desktop.models.analysis import ConflictCandidate, ConflictType

class ConflictAnalyzer:
    """
    Asynchronous heuristic/LLM analyzer.
    Scans active KnowledgeRecords for an identity and proposes ConflictCandidates.
    """
    
    def __init__(self, semantic_disagreement_threshold: float = 0.3):
        self.semantic_disagreement_threshold = semantic_disagreement_threshold
        
    def _text_similarity(self, text1: str, text2: str) -> float:
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    async def analyze(self, identity_uuid: str, records: List[KnowledgeRecord], identity_version: int) -> List[ConflictCandidate]:
        """
        Analyze records bound to an identity for conflicts.
        This is a placeholder for a true semantic LLM analysis.
        """
        candidates = []
        active_records = [r for r in records if r.status == KnowledgeRecordStatus.ACTIVE]
        
        if len(active_records) < 2:
            return candidates
            
        # Very naive heuristic for demonstration:
        # If records under the exact same identity are significantly different in text, flag a factual conflict candidate.
        # In a real system, an LLM would determine if "REST" and "GraphQL" are mutually exclusive for this specific identity.
        
        for i, rec_a in enumerate(active_records):
            for rec_b in active_records[i+1:]:
                sim = self._text_similarity(rec_a.content, rec_b.content)
                if sim < self.semantic_disagreement_threshold:
                    candidate = ConflictCandidate(
                        identity_uuid=identity_uuid,
                        supporting_records=[rec_a.record_id, rec_b.record_id],
                        conflict_type=ConflictType.FACTUAL,
                        reason=f"Semantic divergence detected (similarity={sim:.2f})",
                        confidence=0.85,
                        identity_version=identity_version
                    )
                    candidates.append(candidate)
                    
        return candidates
