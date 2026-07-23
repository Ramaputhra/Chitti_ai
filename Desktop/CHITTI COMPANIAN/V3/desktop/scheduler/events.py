from dataclasses import dataclass
from desktop.models.events import SystemEvent

@dataclass
class WorkflowScheduled(SystemEvent):
    event_type: str = "WorkflowScheduled"
    workflow_id: str = ""

@dataclass
class NodeStarted(SystemEvent):
    event_type: str = "NodeStarted"
    workflow_id: str = ""
    node_id: str = ""

@dataclass
class NodeCompleted(SystemEvent):
    event_type: str = "NodeCompleted"
    workflow_id: str = ""
    node_id: str = ""
    result: str = "SUCCESS"

@dataclass
class NodeFailed(SystemEvent):
    event_type: str = "NodeFailed"
    workflow_id: str = ""
    node_id: str = ""
    reason: str = ""

@dataclass
class WorkflowWaiting(SystemEvent):
    event_type: str = "WorkflowWaiting"
    workflow_id: str = ""
    reason: str = "Waiting for child or delay"

@dataclass
class WorkflowBlocked(SystemEvent):
    event_type: str = "WorkflowBlocked"
    workflow_id: str = ""
    resource: str = ""

@dataclass
class WorkflowPaused(SystemEvent):
    event_type: str = "WorkflowPaused"
    workflow_id: str = ""
    reason: str = ""

@dataclass
class WorkflowResumed(SystemEvent):
    event_type: str = "WorkflowResumed"
    workflow_id: str = ""

@dataclass
class WorkflowFinished(SystemEvent):
    event_type: str = "WorkflowFinished"
    workflow_id: str = ""
    status: str = "COMPLETED"  # COMPLETED, FAILED, CANCELLED
