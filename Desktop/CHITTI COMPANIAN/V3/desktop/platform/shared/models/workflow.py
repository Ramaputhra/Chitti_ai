import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class WorkflowPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TimeoutClass(Enum):
    FAST = 1000          # 1 second
    INTERACTIVE = 5000   # 5 seconds
    BACKGROUND = 30000   # 30 seconds
    LONG_RUNNING = 300000 # 5 minutes


class WorkflowState(Enum):
    CREATED = "Created"
    QUEUED = "Queued"
    RUNNING = "Running"
    RETRYING = "Retrying"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass(frozen=True)
class RetryPolicy:
    """Configures retry behavior for a step or workflow."""
    max_attempts: int = 3
    backoff_ms: int = 1000
    retryable_errors: List[str] = field(default_factory=list)
    timeout_ms: Optional[int] = None


@dataclass(frozen=True)
class ExecutionPolicy:
    """Execution constraints for a workflow step."""
    retry_policy: Optional[RetryPolicy] = field(default_factory=RetryPolicy)
    timeout_class: TimeoutClass = TimeoutClass.INTERACTIVE
    timeout_ms: Optional[int] = None # Overrides timeout_class if set
    idempotent: bool = True
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    requires_approval: bool = False
    approval_prompt: Optional[str] = None


@dataclass(frozen=True)
class WorkflowStep:
    """
    A single logical step in a generated plan.
    Frozen (immutable) — the Executor must not mutate steps mid-flight.
    'action' must be a WorkflowAction primitive string.
    """
    action: str
    step_id: str
    parameters: Dict[str, Any] = field(default_factory=dict, compare=False)
    policy: ExecutionPolicy = field(default_factory=ExecutionPolicy, compare=False)
    
    depends_on: List[str] = field(default_factory=list, compare=False)
    on_failure: Optional[str] = field(default=None, compare=False)
    compensation_step_id: Optional[str] = field(default=None, compare=False)

    def __hash__(self) -> int:
        return hash(self.action)


@dataclass
class Workflow:
    """
    An immutable, fully traceable execution plan produced by the Planner.
    Once created, it is never mutated. If plans change, the Planner creates a new Workflow.
    """
    steps: List[WorkflowStep]
    source_intent: str = "Unknown"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_workflow_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    
    # Versioning
    workflow_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    planner_version: str = "1.0.0"
    runtime_version: str = "1.0.0"

    priority: WorkflowPriority = WorkflowPriority.NORMAL
    state: WorkflowState = WorkflowState.CREATED
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Legacy alias kept for backward-compat while we migrate WorkflowExecutor
    @property
    def id(self) -> str:
        return self.workflow_id

@dataclass
class WorkflowContext:
    """
    Holds orchestration state during workflow execution.
    Owned by the WorkflowRuntime.
    """
    workflow_id: str
    task_id: Optional[str]
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)

