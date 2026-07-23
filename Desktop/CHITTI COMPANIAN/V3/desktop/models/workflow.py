from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from desktop.models.evidence import EvidenceDomain
from desktop.models.identity import Identity, ProjectIdentity

class WorkflowAction(Enum):
    EDIT_FILE = "EDIT_FILE"
    RUN_COMMAND = "RUN_COMMAND"
    COPY_TEXT = "COPY_TEXT"
    OPEN_FOLDER = "OPEN_FOLDER"
    READ_DOCUMENT = "READ_DOCUMENT"
    UNKNOWN = "UNKNOWN"

class WorkflowStage(Enum):
    RESEARCH = "RESEARCH"
    IMPLEMENTATION = "IMPLEMENTATION"
    BUILD = "BUILD"
    TEST = "TEST"
    DEBUG = "DEBUG"
    DOCUMENTATION = "DOCUMENTATION"
    UNKNOWN = "UNKNOWN"

@dataclass
class WorkflowEvent:
    identity: Identity
    domain: EvidenceDomain
    action: WorkflowAction
    stage: WorkflowStage
    start_time: float
    end_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowStatistics:
    research_time_sec: float = 0.0
    coding_time_sec: float = 0.0
    testing_time_sec: float = 0.0
    debug_time_sec: float = 0.0
    build_attempts: int = 0
    failures: int = 0

@dataclass
class ProjectWorkflow:
    project_identity: ProjectIdentity
    events: List[WorkflowEvent] = field(default_factory=list)
    statistics: WorkflowStatistics = field(default_factory=WorkflowStatistics)
    status: str = "InProgress" # e.g. "Completed Successfully", "Ended With Failures"
    
@dataclass
class GeneralWorkflow:
    events: List[WorkflowEvent] = field(default_factory=list)
    statistics: WorkflowStatistics = field(default_factory=WorkflowStatistics)

class OutcomeType(Enum):
    TESTS_PASSING = "TESTS_PASSING"
    TESTS_FAILING = "TESTS_FAILING"
    BUILD_FIXED = "BUILD_FIXED"
    BUILD_FAILED = "BUILD_FAILED"
    IMPLEMENTATION_INTERRUPTED = "IMPLEMENTATION_INTERRUPTED"
    VALIDATION_PENDING = "VALIDATION_PENDING"
    RESEARCH_DOMINANT = "RESEARCH_DOMINANT"

class EvidenceStrength(Enum):
    DETERMINISTIC = "DETERMINISTIC"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class WorkflowOutcome:
    type: OutcomeType
    description: str
    strength: EvidenceStrength
    supporting_events: List[WorkflowEvent] = field(default_factory=list)

@dataclass
class ProjectAssessment:
    workflow: ProjectWorkflow
    outcomes: List[WorkflowOutcome] = field(default_factory=list)
