from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List

class ExecutionStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

@dataclass
class ExecutionContext:
    workflow_id: str
    step_id: str
    capability_id: str
    parameters: Dict[str, Any]
    attempt: int = 1
    timeout: float = 10.0
    telemetry: Dict[str, Any] = field(default_factory=dict)
    runtime_state: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionEvidence:
    source: str # e.g., "OS", "ActivityTimeline", "Accessibility", "Vision"
    status: ExecutionStatus
    confidence: float
    observations: List[str]
    timestamp: float
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CapabilityStartedEvent:
    context: ExecutionContext
    timestamp: float

@dataclass
class CapabilityCompletedEvent:
    context: ExecutionContext
    status: ExecutionStatus
    error_message: str = ""
    timestamp: float = 0.0

@dataclass
class CapabilityOutputAvailableEvent:
    context: ExecutionContext
    output_data: Dict[str, Any]
    timestamp: float

@dataclass
class VerificationStartedEvent:
    context: ExecutionContext
    timestamp: float

@dataclass
class VerificationCompletedEvent:
    context: ExecutionContext
    status: ExecutionStatus
    confidence: float
    evidence: List[ExecutionEvidence] = field(default_factory=list)
    timestamp: float = 0.0

@dataclass
class WorkflowCompletedEvent:
    intent_id: str
    plan_id: str
    status: ExecutionStatus
    timestamp: float

@dataclass
class WorkflowVerifiedEvent:
    """
    Emitted after an entire workflow finishes executing and all steps are verified.
    This is the trigger for ExperienceRuntime to learn from the workflow.
    """
    session_id: str
    trigger_transcript: str
    workflow_steps: List[Dict[str, Any]]
    status: ExecutionStatus
    confidence: float
    learning_source: str = "llm"
    timestamp: float = 0.0
