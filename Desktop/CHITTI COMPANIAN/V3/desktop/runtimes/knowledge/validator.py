import time
from typing import List, Optional
from desktop.models.knowledge import KnowledgeFact, KnowledgeNamespace, KnowledgeLifecycle

class KnowledgeValidator:
    """
    Validates knowledge records before they are stored by the repository.
    Enforces namespace bounds, confidence thresholds, and ensures trace provenance (Rule 269).
    """

    def __init__(self):
        self.min_confidence = 0.1

    def validate_fact(self, fact: KnowledgeFact) -> bool:
        """
        Runs Rule 269 and other integrity checks.
        Returns True if valid, raises ValueError if invalid.
        """
        if not fact.subject or not fact.predicate or not fact.object:
            raise ValueError("KnowledgeFact must have subject, predicate, and object.")
        
        if not fact.source:
            raise ValueError(f"Rule 269 Violation: Fact {fact.id} is missing a source origin.")
            
        if not isinstance(fact.namespace, KnowledgeNamespace):
            raise ValueError("KnowledgeFact must have a valid KnowledgeNamespace.")
            
        if fact.confidence < self.min_confidence:
            raise ValueError(f"Confidence {fact.confidence} is below minimum threshold {self.min_confidence}.")
            
        if fact.lifecycle == KnowledgeLifecycle.CREATED:
            fact.lifecycle = KnowledgeLifecycle.VALIDATED
            
        return True

    def validate_update(self, existing_fact: KnowledgeFact, new_fact: KnowledgeFact) -> KnowledgeFact:
        """
        Enforces Rule 267 (Knowledge is Immutable by Default).
        Prepares a new version of the fact instead of overwriting.
        """
        self.validate_fact(new_fact)
        
        new_fact.version = existing_fact.version + 1
        new_fact.supersedes_id = existing_fact.id
        new_fact.updated_at = time.time()
        
        return new_fact
