import asyncio
from desktop.app.capability_contracts import ICapability, CapabilityDescriptor
from desktop.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus

class FlakyCapability(ICapability):
    """Simulates a capability that fails randomly or times out."""
    def __init__(self):
        self.failures = 0
        
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        mode = context.workflow.parameters.get("mode", "success")
        
        if mode == "timeout":
            await asyncio.sleep(10.0) # Will exceed typical timeout
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
            
        elif mode == "retryable":
            if self.failures < 2:
                self.failures += 1
                return ExecutionResult(status=ExecutionStatus.RETRYABLE_FAILURE, error_message="Network glitch")
            else:
                return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"msg": "Recovered!"})
                
        return ExecutionResult(status=ExecutionStatus.SUCCESS)

def get_flaky_capability_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        id="FlakyCapability",
        version="1.0.0",
        permissions=[],
        execution_mode="async",
        factory=FlakyCapability
    )
