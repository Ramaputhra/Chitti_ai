from abc import ABC, abstractmethod
from typing import Optional, List
from desktop.execution_graph.models import ExecutionNode, RetryPolicy
from desktop.scheduler.models import ScheduledWorkflow
from desktop.execution.models import ExecutionContext, ExecutionError, ExecutionStatus
from desktop.scheduler.decision_engine import SchedulingDecision
from desktop.execution.supervisor.models import TimeoutConfig, FailureSeverity, RecoveryPolicy

class ITimeoutManager(ABC):
    @abstractmethod
    def register_execution(self, execution_id: str, config: TimeoutConfig): pass
    
    @abstractmethod
    def unregister_execution(self, execution_id: str): pass
    
    @abstractmethod
    def record_heartbeat(self, execution_id: str): pass

class IRetryEngine(ABC):
    @abstractmethod
    def evaluate_retry(self, execution_id: str, error: ExecutionError, policy: RetryPolicy) -> Optional[SchedulingDecision]:
        """Returns a SchedulingDecision(RETRY) if retryable, else None."""
        pass

class IRecoveryManager(ABC):
    @abstractmethod
    def cleanup_resources(self, execution_id: str):
        """Guarantees resource release exactly once."""
        pass
        
    @abstractmethod
    def determine_recovery_policy(self, execution_id: str, severity: FailureSeverity) -> RecoveryPolicy: pass

class IExecutionSupervisorRuntime(ABC):
    @abstractmethod
    async def start(self): pass
    
    @abstractmethod
    async def stop(self): pass
    
    @abstractmethod
    def monitor_execution(self, execution_id: str, node: ExecutionNode, context: ExecutionContext): pass
    
    @abstractmethod
    def handle_execution_failure(self, execution_id: str, error: ExecutionError): pass
    
    @abstractmethod
    def handle_orphan_detection(self, execution_id: str): pass
