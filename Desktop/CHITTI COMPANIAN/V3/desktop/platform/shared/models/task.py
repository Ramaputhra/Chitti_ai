import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class TaskState(Enum):
    CREATED = "Created"
    PLANNING = "Planning"
    RUNNING = "Running"
    WAITING = "Waiting"
    REPLANNING = "Replanning"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class ExecutionState(Enum):
    EXECUTING = "Executing"
    PAUSED = "Paused"
    APPROVAL_PENDING = "Approval_Pending"
    RETRYING = "Retrying"
    RECOVERING = "Recovering"

class RecoveryReason(str, Enum):
    PROCESS_CRASH = "Process_Crash"
    SYSTEM_RESTART = "System_Restart"
    USER_RESUME = "User_Resume"
    CHECKPOINT_RESTORE = "Checkpoint_Restore"

class TaskPriority(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"
    BACKGROUND = "Background"

@dataclass
class TaskMetrics:
    active_time: float = 0.0
    waiting_time: float = 0.0
    blocked_time: float = 0.0
    workflow_count: int = 0
    retry_count: int = 0
    checkpoint_count: int = 0

@dataclass
class TaskObservation:
    """An observation recorded after a step executes."""
    step_id: str
    result: str
    success: bool
    timestamp: float = field(default_factory=time.time)

@dataclass
class TaskStepData:
    """
    Technology-neutral representation of a step proposed by the LLM.
    Used by the WorkflowBuilder to create an actual Workflow.
    """
    action_type: str        # e.g., "search", "read", "summarize", "complete"
    parameters: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""     # The thought process that led to this step

@dataclass
class TaskCheckpoint:
    """An immutable snapshot of a task's progress."""
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    workflow_id: str = ""
    completed_step_ids: List[str] = field(default_factory=list)
    observations_hash: str = ""
    planner_version: str = "1.0"
    kernel_version: str = "1.0"
    retry_count: int = 0
    completed_steps: List[TaskStepData] = field(default_factory=list)
    observations: List[TaskObservation] = field(default_factory=list)

@dataclass
class TaskContext:
    """
    Holds the state of a long-running, multi-step goal.
    Owned by the TaskRuntime.
    """
    schema_version: str = "1.0"
    goal: str = ""
    source_intent: str = "Unknown"
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: TaskPriority = TaskPriority.NORMAL
    
    state: TaskState = TaskState.CREATED
    execution_state: ExecutionState = ExecutionState.EXECUTING
    current_state_summary: str = "Initialized"
    
    # Progress tracking (Semantic)
    current_workflow: str = "-"
    current_step: str = "-"
    waiting_on: str = "No"
    estimated_remaining_steps: int = 5
    progress_percentage: float = 0.0
    
    # Template context if this task was instantiated from a template
    template_context: Any = None
    
    completed_steps: List[TaskStepData] = field(default_factory=list)
    observations: List[TaskObservation] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    checkpoints: List[TaskCheckpoint] = field(default_factory=list)
    
    retry_count: int = 0
    max_retries: int = 3
    
    execution_history: List[str] = field(default_factory=list)
    
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Active workflow ID being awaited by the runtime
    active_workflow_id: Optional[str] = None
    
    metrics: TaskMetrics = field(default_factory=TaskMetrics)
