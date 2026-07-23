from desktop.brain.execution.registry import CapabilityExecutionRegistry
from desktop.brain.execution.models import ExecutionStepResult
import time

class CapabilityInvoker:
    def __init__(self, registry: CapabilityExecutionRegistry):
        self.registry = registry
        
    def invoke(self, step, budget: int) -> ExecutionStepResult:
        if budget <= 0:
            return ExecutionStepResult(step.step_id, "FAILED", "", "BUDGET_EXCEEDED", 0)
            
        handler = self.registry.get_handler(step.action_type)
        if not handler:
            return ExecutionStepResult(step.step_id, "FAILED", "", f"No handler for {step.action_type}", 0)
            
        start_time = time.time()
        try:
            status, stdout, stderr = handler(step.payload)
        except Exception as e:
            status, stdout, stderr = "FAILED", "", str(e)
            
        duration = int((time.time() - start_time) * 1000)
        return ExecutionStepResult(step.step_id, status, stdout, stderr, duration)
