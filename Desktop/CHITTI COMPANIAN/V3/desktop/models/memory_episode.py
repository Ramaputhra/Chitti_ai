from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import uuid

class RetentionPolicy(Enum):
    EPHEMERAL = "EPHEMERAL"
    LONG_TERM = "LONG_TERM"
    PERMANENT = "PERMANENT"

@dataclass
class MemoryEpisodeIdentity:
    episode_id: str = field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:12]}")
    source_experience_id: str = ""
    compiler_version: str = "v2.0.0"
    version: int = 1
    parent_episode_id: Optional[str] = None
    experience_fingerprint: str = ""

@dataclass
class MemoryConfidence:
    compiler_confidence: float = 1.0
    evidence_confidence: float = 1.0
    retrieval_confidence: float = 0.0

@dataclass
class MemoryRelationships:
    parent_episodes: List[str] = field(default_factory=list)
    child_episodes: List[str] = field(default_factory=list)
    continuations: List[str] = field(default_factory=list)
    related_episodes: List[str] = field(default_factory=list)
    derived_from: List[str] = field(default_factory=list)
    supersedes: Optional[str] = None

@dataclass
class MemoryEpisodeMetadata:
    temporal_context: List[str] = field(default_factory=list)
    spatial_context: List[str] = field(default_factory=list)
    social_context: List[str] = field(default_factory=list)
    domain_tags: List[str] = field(default_factory=list)

@dataclass
class MemoryEpisode:
    semantic_summary: str
    identity: MemoryEpisodeIdentity
    confidence: MemoryConfidence
    metadata: MemoryEpisodeMetadata
    relationships: MemoryRelationships = field(default_factory=MemoryRelationships)
    importance_score: float = 0.5
    retention_policy: RetentionPolicy = RetentionPolicy.LONG_TERM
