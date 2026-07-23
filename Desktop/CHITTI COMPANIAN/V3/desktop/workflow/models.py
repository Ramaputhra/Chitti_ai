from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from desktop.models.events import SystemEvent

class WorkflowState(Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    WORKFLOW_READY = "WORKFLOW_READY"
    PLANNING = "PLANNING"
    PLANNED = "PLANNED"
    GRAPH_BUILDING = "GRAPH_BUILDING"
    GRAPH_READY = "GRAPH_READY"
    SCHEDULING = "SCHEDULING"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class WorkflowTemplate:
    workflow_id: str
    version: int = 1
    steps: List[Any] = field(default_factory=list)
    name: str = ""
    description: str = ""
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    created_at: float = 0.0
    modified_at: float = 0.0
    last_executed: float = 0.0
    execution_count: int = 0
    estimated_duration_sec: float = 0.0


@dataclass(frozen=True)
class WorkflowContext:
    conversation_id: str = "default_convo"
    speaker_id: str = "owner"
    language: str = "en"
    desktop_session: str = "active"
    authentication_state: str = "verified"
    priority: int = 0

@dataclass(frozen=True)
class WorkflowDefinition:
    instance_id: str
    template_id: str
    intent_id: str
    entities: Dict[str, Any]
    steps: List[str]
    created_at: float
    source: str = "core"
    estimated_complexity: str = "LOW"

@dataclass
class WorkflowStatus:
    state: WorkflowState
    context: WorkflowContext

@dataclass
class WorkflowInstance:
    definition: WorkflowDefinition
    status: WorkflowStatus

@dataclass
class WorkflowLifecycleEvent(SystemEvent):
    event_type: str = "WorkflowLifecycleEvent"
    instance: Optional[WorkflowInstance] = None

@dataclass
class WorkflowCreated(WorkflowLifecycleEvent):
    event_type: str = "WorkflowCreated"

@dataclass
class WorkflowValidated(WorkflowLifecycleEvent):
    event_type: str = "WorkflowValidated"

@dataclass
class WorkflowReady(WorkflowLifecycleEvent):
    event_type: str = "WorkflowReady"

@dataclass
class WorkflowCancelled(WorkflowLifecycleEvent):
    event_type: str = "WorkflowCancelled"


@dataclass
class WorkflowFailed(WorkflowLifecycleEvent):
    event_type: str = "WorkflowFailed"
    reason: str = ""

@dataclass
class WorkflowCompleted(WorkflowLifecycleEvent):
    event_type: str = "WorkflowCompleted"
