from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time

from desktop.workflow.models import WorkflowDefinition
from desktop.execution_graph.models import ExecutionGraph
from desktop.core.cancellation import CancellationContext

class SchedulerState(Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ResourceCategory(Enum):
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    VIRTUAL = "VIRTUAL"
    EXTERNAL = "EXTERNAL"

class ResourceState(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    FAILED = "FAILED"

class PreemptionLevel(Enum):
    NONE = "NONE"
    COOPERATIVE = "COOPERATIVE"
    CHECKPOINT = "CHECKPOINT"
    FORCED = "FORCED"

class PriorityClass(Enum):
    SYSTEM = 100
    CRITICAL = 80
    INTERACTIVE = 60
    USER_VISIBLE = 40
    BACKGROUND = 20
    MAINTENANCE = 0

class SchedulerPolicyProfile(Enum):
    INTERACTIVE = "INTERACTIVE"
    BALANCED = "BALANCED"
    POWER_SAVING = "POWER_SAVING"
    HIGH_THROUGHPUT = "HIGH_THROUGHPUT"

@dataclass(frozen=True)
class ResourcePolicy:
    preemptible: bool
    sharable: bool
    queue_limit: int
    idle_timeout: float

@dataclass
class SchedulerMetrics:
    dispatch_latency: float = 0.0
    queue_time: float = 0.0
    preemption_count: int = 0
    resume_count: int = 0
    deadline_misses: int = 0
    average_priority: float = 0.0

@dataclass(frozen=True)
class ResourceLock:
    lock_id: str
    workflow_id: str
    execution_id: str
    node_id: str
    resource_id: str
    acquired_at: float
    expires_at: float
    priority: int

@dataclass(frozen=True)
class ResourceReservation:
    reservation_id: str
    workflow_id: str
    execution_id: str
    resource_id: str
    expires_at: float

@dataclass
class ResourceMetrics:
    average_wait_time: float = 0.0
    maximum_wait_time: float = 0.0
    lock_contention: int = 0
    utilization: float = 0.0
    reservation_failures: int = 0
    preemption_count: int = 0

@dataclass
class WorkflowMetrics:
    created_at: float = field(default_factory=time.time)
    scheduled_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    total_runtime: float = 0.0
    wait_time: float = 0.0
    blocked_time: float = 0.0
    retry_count: int = 0
    resource_wait_time: float = 0.0

from desktop.core.cancellation import CancellationContext

@dataclass(frozen=True)
class ExecutionContext:
    workflow_id: str = "none"
    execution_id: str = "unknown"
    trace_id: str = "unknown"
    conversation_id: str = "default_convo"
    speaker_id: str = "unknown"
    language: str = "en"
    session_id: str = "default_session"
    authentication_state: str = "verified"
    priority: int = 0
    deadline: Optional[float] = None
    cancellation_context: Optional[CancellationContext] = None

@dataclass
class ScheduledWorkflow:
    definition: WorkflowDefinition
    execution_graph: ExecutionGraph
    execution_context: ExecutionContext
    scheduler_state: SchedulerState = SchedulerState.READY
    current_node_id: Optional[str] = None
    acquired_resources: List[str] = field(default_factory=list)
    cancellation_context: Optional[CancellationContext] = None
    metrics: WorkflowMetrics = field(default_factory=WorkflowMetrics)
    parent_workflow_id: Optional[str] = None
    soft_deadline: Optional[float] = None
    hard_deadline: Optional[float] = None

@dataclass(frozen=True)
class SchedulerPolicy:
    max_concurrent_workflows: int = 10
    preemption_enabled: bool = True
    default_node_timeout_sec: int = 30
    workflow_timeout: int = 3600
    deadlock_detection: bool = True
    resource_acquire_timeout: int = 10
    max_retry: int = 3
    heartbeat_interval: float = 1.0
