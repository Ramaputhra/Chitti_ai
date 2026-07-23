from desktop.runtimes.capability.registry import CapabilityRegistry
from desktop.runtimes.capability.adapter import CapabilityAdapter
from desktop.runtimes.capability.context import CapabilityContext
from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus, ExecutionErrorCode
import logging

logger = logging.getLogger(__name__)

class CapabilityInvoker:
    """
    Instantiates capability from descriptor and executes via adapter.
    """
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
        
    async def invoke(self, action_name: str, parameters: dict, context: CapabilityContext) -> ExecutionResult:
        descriptor = self.registry.resolve_by_action_name(action_name)
        if not descriptor:
            descriptor = self.registry.resolve(action_name)
            
        if not descriptor:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"No capability found for action: {action_name}",
                error_code=ExecutionErrorCode.NOT_IMPLEMENTED
            )
            
        if not descriptor.factory:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"No factory defined for capability: {action_name}",
                error_code=ExecutionErrorCode.UNKNOWN_ERROR
            )
            
        # 1. Instantiate the capability
        try:
            capability_instance = descriptor.factory()
        except Exception as e:
            logger.exception(f"Failed to instantiate capability: {action_name}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"Instantiation failed: {e}",
                error_code=ExecutionErrorCode.UNKNOWN_ERROR
            )
        
        # 2. Assign parameters to payload
        context.payload.data = parameters or {}
        
        # 3. Execute via adapter
        result = await CapabilityAdapter.execute_safe(capability_instance, context)
        
        return result
