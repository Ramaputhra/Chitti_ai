from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class CapabilityRisk(Enum):
    SAFE = "SAFE"             # Harmless read operations, trivial actions
    CAUTION = "CAUTION"       # Modifies user data slightly, e.g., rename, move
    PRIVILEGED = "PRIVILEGED" # Destructive or high-impact, e.g., delete files, shutdown
    RESTRICTED = "RESTRICTED" # Security/System critical, e.g., format drive, edit registry. NEVER auto-promoted.

@dataclass
class GeneralizedWorkflow:
    """A parameterized graph of primitives."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    parameters: Dict[str, Any]

@dataclass
class CapabilityVersion:
    version_id: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    promoted_at: Optional[datetime] = None
    supersedes_version: Optional[int] = None
    success_rate: float = 0.0

class CapabilityStatus(Enum):
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    PROMOTED = "PROMOTED"

@dataclass
class CapabilityMetadata:
    id: str
    name: str
    description: str
    created_by: str  # developer, adaptive_learning, imported
    version: int
    risk: CapabilityRisk
    tags: List[str]
    requires: List[str]
    last_verified: Optional[datetime] = None
    success_rate: float = 0.0
    times_used: int = 0
    language_independent: bool = True

@dataclass
class CapabilityCandidate:
    candidate_id: str
    name: str
    workflow: GeneralizedWorkflow
    risk_level: CapabilityRisk
    version: CapabilityVersion
    status: CapabilityStatus = CapabilityStatus.CANDIDATE
    success_count: int = 0
    failure_count: int = 0
    verification_criteria: str = ""
    metadata: Optional[CapabilityMetadata] = None

@dataclass
class PromotionDecision:
    promoted: bool
    reason: str
    requires_human: bool = False
