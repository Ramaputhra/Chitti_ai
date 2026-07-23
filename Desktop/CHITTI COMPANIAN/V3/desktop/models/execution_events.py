from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class ExecutionEvent:
    """Base class for all immutable execution observations."""
    event_id: str
    workflow_id: str
    plan_id: str
    correlation_id: str
    sequence_number: int
    timestamp: datetime

@dataclass(frozen=True)
class TaskStartedEvent(ExecutionEvent):
    task_id: str
    capability_id: str

@dataclass(frozen=True)
class CapabilityInvokedEvent(ExecutionEvent):
    task_id: str
    capability_id: str
    version: Optional[str]
    input_parameters: Dict[str, Any]
    invocation_id: str

@dataclass(frozen=True)
class TaskProgressEvent(ExecutionEvent):
    task_id: str
    capability_id: str
    progress_percentage: float
    status_message: str

@dataclass(frozen=True)
class TaskCompletedEvent(ExecutionEvent):
    task_id: str
    capability_id: str
    output_data: Dict[str, Any]
    duration_ms: float

@dataclass(frozen=True)
class TaskFailedEvent(ExecutionEvent):
    task_id: str
    capability_id: str
    error_code: str
    error_message: str
    retry_count: int

@dataclass(frozen=True)
class WorkflowStartedEvent(ExecutionEvent):
    pass

@dataclass(frozen=True)
class WorkflowCompletedEvent(ExecutionEvent):
    duration_ms: float

@dataclass(frozen=True)
class WorkflowFailedEvent(ExecutionEvent):
    failed_task_id: Optional[str]
    reason: str
