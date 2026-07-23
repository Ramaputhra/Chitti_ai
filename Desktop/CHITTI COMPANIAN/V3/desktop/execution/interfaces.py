from abc import ABC, abstractmethod
from typing import Dict, Any, Mapping
from desktop.execution.models import CapabilityDescriptor, CapabilityResult, ExecutionResult
from desktop.scheduler.models import ExecutionContext
from desktop.execution_graph.models import ExecutionNode
from desktop.core.cancellation import CancellationContext

class ICapabilityRuntime(ABC):
    @abstractmethod
    def get_descriptor(self) -> CapabilityDescriptor:
        """Returns metadata about what this capability can do and what resources it needs."""
        pass

    @abstractmethod
    def health_check(self) -> str:  # Returns CapabilityHealth.value
        pass

    @abstractmethod
    async def execute(self, inputs: Mapping[str, Any], context: ExecutionContext) -> CapabilityResult:
        """
        Performs the isolated business logic. Returns strongly typed CapabilityResult.
        ExecutionRuntime wraps this output in an ExecutionResult.
        """
        pass

class ExecutionDispatcher(ABC):
    @abstractmethod
    def resolve(self, descriptor: CapabilityDescriptor) -> ICapabilityRuntime:
        """Resolves the requested capability descriptor into an executable runtime interface."""
        pass

class IExecutionRuntime(ABC):
    @abstractmethod
    async def execute_node(self, node: ExecutionNode, context: ExecutionContext) -> ExecutionResult:
        """
        Executes a single node by routing it through the Dispatcher to a CapabilityRuntime.
        Guarantees resource release upon completion/failure.
        """
        pass
    
    @abstractmethod
    def cancel_execution(self, execution_id: str, cancellation_context: CancellationContext):
        """Cancels a specific execution via its unique ID."""
        pass
