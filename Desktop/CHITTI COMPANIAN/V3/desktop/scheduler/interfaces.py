from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from desktop.scheduler.models import ScheduledWorkflow
from desktop.execution_graph.models import ResourceRequirement
from desktop.models.events import SystemEvent

from desktop.scheduler.models import ResourceLock, ResourceReservation

@dataclass
class ResourceAcquireResult:
    success: bool
    granted_resources: List[ResourceLock] = field(default_factory=list)
    blocked_resources: List[str] = field(default_factory=list)
    reason: Optional[str] = None
    retry_after: float = 0.0

@dataclass
class ResourceReserveResult:
    success: bool
    reservations: List[ResourceReservation] = field(default_factory=list)
    blocked_resources: List[str] = field(default_factory=list)

class IResourceArbitrator(ABC):
    @abstractmethod
    async def acquire(self, workflow_id: str, execution_id: str, node_id: str, resources: List[ResourceRequirement], priority: int) -> ResourceAcquireResult: pass
    
    @abstractmethod
    async def reserve(self, workflow_id: str, execution_id: str, resources: List[ResourceRequirement], priority: int) -> ResourceReserveResult: pass

    @abstractmethod
    def release_all(self, workflow_id: str): pass

class PriorityScheduler(ABC):
    @abstractmethod
    async def handle_event(self, event: SystemEvent): 
        """The primary entry point. The Scheduler reacts to EventBus events."""
        pass
    
    @abstractmethod
    def submit_workflow(self, workflow: ScheduledWorkflow): pass
    
    @abstractmethod
    def execute_decision(self, decision: 'SchedulingDecision'):
        """Executes a decision rendered by the SchedulingDecisionEngine."""
        pass

    @abstractmethod
    def cancel_workflow(self, workflow_id: str, reason: str, cancelled_by: str): pass
    
    @abstractmethod
    def pause_workflow(self, workflow_id: str, reason: str): pass
    
    @abstractmethod
    def resume_workflow(self, workflow_id: str): pass
