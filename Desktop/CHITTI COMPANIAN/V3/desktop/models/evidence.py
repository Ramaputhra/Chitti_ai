from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from desktop.models.identity import Identity

class EvidenceDomain(Enum):
    RESEARCH = "research"
    ARTIFACT = "artifact"
    ACTION = "action"
    EXTRACTION = "extraction"
    COMMUNICATION = "communication"
    MEDIA = "media"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class EvidenceSource:
    source_id: str
    provider: str
    timestamp: float
    confidence: float
    raw_reference: Any

@dataclass
class EvidenceCluster:
    label: str
    identity: Identity
    importance_score: float = 0.0
    duration: float = 0.0
    sources: List[EvidenceSource] = field(default_factory=list)

@dataclass
class RedundantEvidence:
    label: str
    count: int
    sources: List[EvidenceSource] = field(default_factory=list)

@dataclass
class ProviderEvidence:
    clusters: List[EvidenceCluster] = field(default_factory=list)
    redundancies: List[RedundantEvidence] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IdentityEvidence:
    """Base class for cross-provider synthesized evidence (Rule 51)."""
    identity: Identity
    importance_score: float = 0.0
    duration: float = 0.0
    clusters_by_domain: Dict[EvidenceDomain, List[EvidenceCluster]] = field(default_factory=dict)

@dataclass
class ProjectEvidence(IdentityEvidence):
    pass

@dataclass
class EpisodeSection:
    provider: str
    clusters: List[EvidenceCluster] = field(default_factory=list)
    redundancies: List[RedundantEvidence] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
