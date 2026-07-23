from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

class AnalysisType(Enum):
    CONFLICT = "CONFLICT"
    CONSENSUS = "CONSENSUS"
    TRUST = "TRUST"
    GRAPH_MAINTENANCE = "GRAPH_MAINTENANCE"

class AnalysisStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    STALE = "STALE"

@dataclass(frozen=True)
class AnalysisDescriptor:
    analysis_type: AnalysisType
    dependencies: List[AnalysisType] = field(default_factory=list)
    priority: int = 1
    supports_incremental: bool = False
    supports_parallel: bool = False

class ConflictType(Enum):
    FACTUAL = "FACTUAL"
    TEMPORAL = "TEMPORAL"
    SOURCE = "SOURCE"
    VERSION = "VERSION"
    AMBIGUOUS = "AMBIGUOUS"
    MUTUALLY_EXCLUSIVE = "MUTUALLY_EXCLUSIVE"

class ConflictStatus(Enum):
    OPEN = "OPEN"
    VALIDATING = "VALIDATING"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"
    SUPERSEDED = "SUPERSEDED"
    STALE = "STALE"

@dataclass(frozen=True)
class KnowledgeAnalysisTask:
    task_id: str
    identity_uuid: str
    analysis_type: AnalysisType
    priority: int
    status: AnalysisStatus
    requested_at: datetime = field(default_factory=datetime.now)
    identity_version: int = 1

@dataclass(frozen=True)
class KnowledgeAnalysisState:
    identity_uuid: str
    analysis_type: AnalysisType
    status: AnalysisStatus
    last_updated: datetime
    identity_version: int

@dataclass(frozen=True)
class ConflictCandidate:
    identity_uuid: str
    supporting_records: List[str]
    conflict_type: ConflictType
    reason: str
    confidence: float
    identity_version: int

class ConflictSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass(frozen=True)
class KnowledgeConflict:
    conflict_id: str
    identity_uuid: str
    supporting_records: List[str]
    conflict_type: ConflictType
    conflict_description: str
    confidence: float
    status: ConflictStatus = ConflictStatus.OPEN
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    identity_version: int = 1

@dataclass(frozen=True)
class TrustAssessment:
    source_id: str
    score: float
    reason: str
    identity_version: int
    computed_at: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class ConsensusAssessment:
    identity_uuid: str
    agreement_score: float
    agreement_groups: int
    confidence: float
    identity_version: int
    computed_at: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class KnowledgeHealth:
    identity_uuid: str
    conflict_status: ConflictStatus
    trust_status: AnalysisStatus
    consensus_status: AnalysisStatus
    last_analysis: datetime
    overall_health: float
