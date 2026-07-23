from dataclasses import dataclass
from desktop.models.events import SystemEvent
from desktop.execution.supervisor.models import FailureSeverity, RecoveryPolicy

@dataclass
class ExecutionHeartbeat(SystemEvent):
    event_type: str = "ExecutionHeartbeat"
    execution_id: str = ""
    workflow_id: str = ""
    node_id: str = ""
    progress_percentage: float = 0.0

@dataclass
class ExecutionRecovered(SystemEvent):
    event_type: str = "ExecutionRecovered"
    execution_id: str = ""
    workflow_id: str = ""
    recovery_policy: str = ""

@dataclass
class ExecutionEscalated(SystemEvent):
    event_type: str = "ExecutionEscalated"
    execution_id: str = ""
    workflow_id: str = ""
    severity: str = ""
    reason: str = ""

@dataclass
class ExecutionOrphanDetected(SystemEvent):
    event_type: str = "ExecutionOrphanDetected"
    execution_id: str = ""
    workflow_id: str = ""
    last_heartbeat: float = 0.0

@dataclass
class ExecutionCleanupCompleted(SystemEvent):
    event_type: str = "ExecutionCleanupCompleted"
    execution_id: str = ""
    workflow_id: str = ""
    resources_released: int = 0
