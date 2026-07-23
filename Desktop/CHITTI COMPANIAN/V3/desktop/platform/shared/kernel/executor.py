from typing import Any

from desktop.platform.shared.kernel.models import CancellationToken, ExecutionContext, ExecutionResult
from desktop.platform.shared.models.workflow import WorkflowStep
from desktop.runtimes.capability.invoker import CapabilityInvoker

class WorkflowExecutor:
    """
    The Executor executes steps. Nothing else.
    Rule 26: No decision logic (if memory_hit: skip_llm).
    Rule 27: Workflow steps are atomic.
    """
    def __init__(self, capability_invoker: CapabilityInvoker = None):
        self.capability_invoker = capability_invoker
    
    def execute(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        cancellation_token: CancellationToken
    ) -> ExecutionResult:
        """
        Frozen interface for step execution.
        Routes the step to the appropriate runtime based on the step.action.
        """
        if cancellation_token.cancelled:
            return ExecutionResult(
                success=False,
                error=f"Cancelled: {cancellation_token.reason}",
                metrics={"cancelled": True}
            )

        # For Sprint 15, we only have the Capability Runtime.
        # So we route everything there for now.
        if self.capability_invoker:
            return self.capability_invoker.invoke(step, context, cancellation_token)
            
        # Fallback if no invoker
        return ExecutionResult(
            success=False,
            error="No CapabilityInvoker configured.",
            duration_ms=0
        )
