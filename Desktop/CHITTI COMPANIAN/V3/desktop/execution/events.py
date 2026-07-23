from dataclasses import dataclass
from desktop.models.events import SystemEvent
from desktop.execution.models import ExecutionStatus

@dataclass
class ExecutionStarted(SystemEvent):
    event_type: str = "ExecutionStarted"
    execution_id: str = ""
    node_id: str = ""

@dataclass
class ExecutionCompleted(SystemEvent):
    event_type: str = "ExecutionCompleted"
    execution_id: str = ""
    node_id: str = ""
    status: ExecutionStatus = ExecutionStatus.SUCCESS

@dataclass
class ExecutionCancelled(SystemEvent):
    event_type: str = "ExecutionCancelled"
    execution_id: str = ""
    node_id: str = ""
    reason: str = ""

@dataclass
class ExecutionTimedOut(SystemEvent):
    event_type: str = "ExecutionTimedOut"
    execution_id: str = ""
    node_id: str = ""

@dataclass
class ExecutionProgress(SystemEvent):
    event_type: str = "ExecutionProgress"
    execution_id: str = ""
    node_id: str = ""
    progress_percentage: int = 0
    status_message: str = ""
