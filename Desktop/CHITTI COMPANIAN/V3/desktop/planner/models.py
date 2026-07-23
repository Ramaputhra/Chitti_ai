from dataclasses import dataclass, field
from typing import List, Dict, Any
from desktop.workflow.models import WorkflowInstance, WorkflowState
from desktop.models.events import SystemEvent

@dataclass(frozen=True)
class PlannedStep:
    id: str
    capability: str
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class PlannedWorkflow:
    instance_id: str
    steps: List[PlannedStep] = field(default_factory=list)

@dataclass
class WorkflowPlanningStarted(SystemEvent):
    event_type: str = "WorkflowPlanningStarted"
    instance: WorkflowInstance = None

@dataclass
class WorkflowPlanningCompleted(SystemEvent):
    event_type: str = "WorkflowPlanningCompleted"
    instance: WorkflowInstance = None
    planned_workflow: PlannedWorkflow = None

@dataclass
class PlannerValidationFailed(SystemEvent):
    event_type: str = "PlannerValidationFailed"
    instance: WorkflowInstance = None
    reason: str = ""
