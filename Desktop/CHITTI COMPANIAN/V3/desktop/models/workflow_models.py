from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List

from desktop.models.planner_models import ExecutionGoal

class WorkflowStepStatus(Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"

@dataclass
class WorkflowContext:
    """
    Shared state context passed between steps in a workflow.
    Keeps capabilities entirely stateless.
    """
    workflow_id: str
    execution_goal: ExecutionGoal
    variables: Dict[str, Any] = field(default_factory=dict)
    step_outputs: Dict[str, Any] = field(default_factory=dict)
    verification_results: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    started_at: float = 0.0
