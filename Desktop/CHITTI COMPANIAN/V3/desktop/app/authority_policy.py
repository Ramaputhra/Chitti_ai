from desktop.models.memory import KnowledgeSource, AuthorityTier, SourceType
from desktop.models.cognition import AuthorityAssessment

class AuthorityPolicy:
    """
    Deterministic policy for assigning authority to a source.
    Authority is an immutable property assigned based on the source's origin and metadata,
    and never derived from the actual content or future track record.
    """
    
    def __init__(self):
        self.version = "1.0"
        
    def evaluate(self, source: KnowledgeSource) -> AuthorityAssessment:
        # Default starting tier
        tier = AuthorityTier.NEUTRAL
        reason = "Default neutral authority."
        
        # Example policy logic
        if source.source_type == SourceType.SPECIFICATION and "official" in source.origin.lower():
            tier = AuthorityTier.OFFICIAL
            reason = "Official specifications carry maximum authority."
        elif source.source_type == SourceType.DOCUMENTATION:
            tier = AuthorityTier.HIGH
            reason = "Documentation implies structured intent."
        elif source.source_type == SourceType.WEB_SCRAPE:
            tier = AuthorityTier.LOW
            reason = "Unverified web scrapes default to low authority."
            
        return AuthorityAssessment(
            source_id=source.source_id,
            tier=tier,
            reason=reason,
            policy_version=self.version
        )
