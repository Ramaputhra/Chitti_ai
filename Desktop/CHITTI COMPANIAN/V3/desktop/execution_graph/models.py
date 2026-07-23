from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from enum import Enum

from desktop.models.events import SystemEvent

if TYPE_CHECKING:
    from desktop.workflow.models import WorkflowInstance

class ExecutionNodeType(Enum):
    CAPABILITY = "CAPABILITY"
    DECISION = "DECISION"
    PARALLEL = "PARALLEL"
    DELAY = "DELAY"
    RETRY = "RETRY"
    WAIT = "WAIT"
    CONFIRMATION = "CONFIRMATION"
    SPEAK = "SPEAK"

class NodeState(Enum):
    READY = "READY"
    RESOURCE_WAIT = "RESOURCE_WAIT"
    RUNNING = "RUNNING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"

class RetryStrategy(Enum):
    EXPONENTIAL = "EXPONENTIAL"
    LINEAR = "LINEAR"
    NONE = "NONE"

@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 0
    strategy: RetryStrategy = RetryStrategy.NONE
    delay: float = 0.0

class ResourceAccessMode(Enum):
    EXCLUSIVE = "EXCLUSIVE"
    SHARED_READ = "SHARED_READ"
    SHARED_WRITE = "SHARED_WRITE"

@dataclass(frozen=True)
class ResourceRequirement:
    resource: str
    mode: ResourceAccessMode = ResourceAccessMode.EXCLUSIVE
    timeout: int = 5
    optional: bool = False

@dataclass(frozen=True)
class ResourceBundle:
    bundle_id: str
    resources: List[ResourceRequirement] = field(default_factory=list)

@dataclass(frozen=True)
class ExecutionNode:
    node_id: str
    node_type: ExecutionNodeType
    capability: Optional[str]
    inputs: Dict[str, Any] = field(default_factory=dict)
    required_resources: List[ResourceRequirement] = field(default_factory=list)
    resource_bundles: List[ResourceBundle] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 30
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    parallel: bool = False

@dataclass(frozen=True)
class ExecutionGraph:
    nodes: List[ExecutionNode] = field(default_factory=list)

@dataclass
class ExecutionGraphBuildingStarted(SystemEvent):
    event_type: str = "ExecutionGraphBuildingStarted"
    instance: Optional['WorkflowInstance'] = None

@dataclass
class ExecutionGraphReady(SystemEvent):
    event_type: str = "ExecutionGraphReady"
    instance: Optional['WorkflowInstance'] = None
    graph: Optional[ExecutionGraph] = None

@dataclass
class GraphValidationFailed(SystemEvent):
    event_type: str = "GraphValidationFailed"
    instance: Optional['WorkflowInstance'] = None
    reason: str = ""

@dataclass
class WorkflowReadyForScheduling(SystemEvent):
    event_type: str = "WorkflowReadyForScheduling"
    instance: Optional['WorkflowInstance'] = None
