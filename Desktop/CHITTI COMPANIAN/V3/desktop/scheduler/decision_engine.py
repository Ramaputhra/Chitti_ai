from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from desktop.scheduler.models import ScheduledWorkflow, ResourceState

class SchedulingAction(Enum):
    RUN = "RUN"
    WAIT = "WAIT"
    PAUSE = "PAUSE"
    PREEMPT = "PREEMPT"
    CANCEL = "CANCEL"
    RESUME = "RESUME"
    RETRY = "RETRY"

class DecisionReason(Enum):
    HIGHER_PRIORITY = "HIGHER_PRIORITY"
    DEADLINE = "DEADLINE"
    STARVATION = "STARVATION"
    RESOURCE_AVAILABLE = "RESOURCE_AVAILABLE"
    RESOURCE_BLOCKED = "RESOURCE_BLOCKED"
    USER_REQUEST = "USER_REQUEST"
    RETRY = "RETRY"
    RESUME = "RESUME"
    TIMEOUT = "TIMEOUT"

@dataclass(frozen=True)
class DecisionTrace:
    decision_id: str
    workflow_id: str
    node_id: str
    base_priority: int
    effective_priority: int
    decision_reason: DecisionReason
    resource_snapshot_id: str
    policy_profile: str
    timestamp: float

@dataclass(frozen=True)
class SchedulingDecision:
    action: SchedulingAction
    workflow_id: str
    node_id: str
    reason: DecisionReason
    effective_priority: int
    trace: Optional[DecisionTrace] = None

@dataclass(frozen=True)
class ResourceSnapshot:
    """Read-only view of resource availability at decision time."""
    availability: Dict[str, ResourceState] = field(default_factory=dict)
    
class SchedulingDecisionEngine(ABC):
    @abstractmethod
    def select_next_node(
        self, 
        ready_queue: List[ScheduledWorkflow], 
        running_workflows: List[ScheduledWorkflow],
        resource_snapshot: ResourceSnapshot
    ) -> Optional[SchedulingDecision]:
        """
        Evaluates slack time, aging, priority, and resource bonuses to pick the optimal next node.
        """
        pass
        
    @abstractmethod
    def evaluate_preemption(
        self, 
        incoming_workflow: ScheduledWorkflow, 
        running_workflows: List[ScheduledWorkflow],
        resource_snapshot: ResourceSnapshot
    ) -> List[SchedulingDecision]:
        """
        Returns a list of PREEMPT or PAUSE decisions if running workflows must yield to the incoming task.
        """
        pass
