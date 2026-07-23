from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from desktop.models.cognition import ExecutionPlan, WorkflowRequest, ApprovalRequirement
from desktop.models.interaction import InteractionEnvelope
from desktop.app.context import ServiceRegistry

class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    TIMED_OUT = "TIMED_OUT"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    CANCELLED = "CANCELLED"

class ExecutionErrorCode(str, Enum):
    # System Errors
    ACCESS_DENIED = "ACCESS_DENIED"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    MISSING_REQUIRED_PARAMETER = "MISSING_REQUIRED_PARAMETER"
    
    # File System Errors
    PATH_NOT_FOUND = "PATH_NOT_FOUND"
    SOURCE_NOT_FOUND = "SOURCE_NOT_FOUND"
    FILE_ALREADY_EXISTS = "FILE_ALREADY_EXISTS"
    DESTINATION_LOCKED = "DESTINATION_LOCKED"
    INVALID_PATH = "INVALID_PATH"
    USE_MOVE_CAPABILITY = "USE_MOVE_CAPABILITY"

@dataclass
class ExecutionResult:
    """The outcome of a capability execution."""
    status: ExecutionStatus
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[ExecutionErrorCode] = None
    version: str = "1.0"


@dataclass
class ExecutionContext:
    """
    Immutable context passed to Capabilities.
    Contains strictly the information needed to execute, without exposing the Kernel.
    """
    plan: ExecutionPlan
    workflow: WorkflowRequest
    correlation_id: str
    interaction_id: str
    attempt: int
    deadline: Optional[datetime]
    services: ServiceRegistry

@dataclass
class WorkflowContext:
    """
    Mutable state tracker for a specific execution plan.
    (Rule 177: Execution may track state here, but never alters the ExecutionPlan).
    """
    plan_id: str
    correlation_id: str
    execution_state: ExecutionStatus = ExecutionStatus.WAITING_APPROVAL
    attempt_count: int = 0
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[ExecutionResult] = None

@dataclass
class ExecutionStep:
    """A granular record of a single capability invocation within a trace."""
    step_id: str
    capability_name: str
    status: ExecutionStatus
    start_time: float
    end_time: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retries: int = 0
    version: str = "1.0"

@dataclass
class ExecutionTrace:
    """Records the end-to-end chronological execution path of a completed ExecutionPlan."""
    trace_id: str
    plan_id: str
    steps: list[ExecutionStep] = field(default_factory=list)
    total_duration_ms: float = 0.0
    overall_status: ExecutionStatus = ExecutionStatus.WAITING_APPROVAL
    cancellation_reason: Optional[str] = None
    version: str = "1.0"

