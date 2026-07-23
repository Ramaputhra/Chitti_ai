import logging
import time
from typing import Any

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.cognition import ExecutionPlan, WorkflowRequest
from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
from desktop.app.context import KernelContext
from desktop.runtimes.verification_runtime import VerificationRuntime, VerificationStatus

logger = logging.getLogger(__name__)

class WorkflowRuntime(IRuntime):
    """
    Rule 26: Workflow Owns Orchestration.
    Executes a WorkflowPlan through a robust state machine (Pending -> Executing -> Verifying -> Completed).
    """
    
    def __init__(self, capability_runtime: Any, verification_runtime: VerificationRuntime):
        self.capability_runtime = capability_runtime
        self.verification_runtime = verification_runtime
        self.context = None

    @property
    def dependencies(self):
        return [self.capability_runtime, self.verification_runtime]

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        # Subscribes to ExecutionPlan to intercept the execution pipeline
        self.context.event_bus.subscribe(ExecutionPlan, self._on_plan)
        return True

    async def start(self) -> bool:
        logger.info("[WorkflowRuntime] Started. Subscribed to ExecutionPlan.")
        print("    [WorkflowRuntime] Started. Subscribed to ExecutionPlan.")
        return True

    async def stop(self) -> bool:
        logger.info("[WorkflowRuntime] Stopped.")
        print("    [WorkflowRuntime] Stopped.")
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    async def _on_plan(self, plan: ExecutionPlan):
        """Intercepts the plan and enforces orchestration."""
        logger.info(f"[WorkflowRuntime] Intercepted ExecutionPlan")
        import uuid
        from datetime import datetime
        from desktop.models.execution import ExecutionTrace, ExecutionStep, ExecutionStatus as LegacyExecutionStatus
        from desktop.models.events import ExecutionCompletedEvent

        trace = ExecutionTrace(
            trace_id=str(uuid.uuid4()),
            plan_id=getattr(plan, 'plan_id', 'unknown')
        )
        start_time_total = time.time()
        
        for workflow in plan.workflows:
            step_start = time.time()
            success, result = await self._execute_step(plan, workflow)
            
            step = ExecutionStep(
                step_id=str(uuid.uuid4()),
                capability_name=workflow.action,
                status=LegacyExecutionStatus.SUCCESS if success else LegacyExecutionStatus.FAILED,
                start_time=step_start,
                end_time=time.time(),
                parameters=getattr(workflow, "parameters", {}) or {},
                output_payload=getattr(result, "outputs", {}) if result and hasattr(result, "outputs") else {},
                error_message=getattr(result, "error_message", None) if result and hasattr(result, "error_message") else None
            )
            trace.steps.append(step)

            if not success:
                logger.warning(f"[WorkflowRuntime] ExecutionPlan aborted due to failure in {workflow.action}.")
                trace.overall_status = LegacyExecutionStatus.FAILED
                break
        else:
            trace.overall_status = LegacyExecutionStatus.SUCCESS

        trace.total_duration_ms = (time.time() - start_time_total) * 1000

        # Emit ExecutionCompletedEvent for Verification and Telemetry
        event = ExecutionCompletedEvent(
            timestamp=datetime.now(),
            source="WorkflowRuntime",
            correlation_id=plan.workflows[0].correlation_id if plan.workflows else "",
            event_type="EXECUTION_COMPLETED",
            metadata={
                "status": trace.overall_status.value,
                "duration_ms": trace.total_duration_ms,
                "execution_trace": trace
            }
        )
        if self.context and self.context.event_bus:
            self.context.event_bus.publish(event)
            
        logger.info(f"[WorkflowRuntime] ExecutionPlan processing complete.")
        
    async def _execute_step(self, plan: ExecutionPlan, workflow: WorkflowRequest):
        try:
            logger.info(f"[WorkflowRuntime] Orchestrating step: {workflow.action}")
            
            # 1. Execute capability (Delegated to ExecutionRuntime)
            result = await self.capability_runtime._execute_workflow(plan, workflow)
            
            if not isinstance(result, ExecutionResult):
                logger.error(f"[WorkflowRuntime] Expected ExecutionResult, got {type(result)}. Forcing failure.")
                return False, None
                
            # 2. Verify result (Delegated to VerificationRuntime)
            logger.info(f"[WorkflowRuntime] Verifying step: {workflow.action}")
            verified_result = await self.verification_runtime.verify(result)
            
            if verified_result.status == VerificationStatus.VERIFIED_SUCCESS:
                logger.info(f"[WorkflowRuntime] ✅ Step {workflow.action} fully verified.")
                return True, result
            elif verified_result.status == VerificationStatus.VERIFICATION_NOT_SUPPORTED:
                logger.info(f"[WorkflowRuntime] ⚠️ Step {workflow.action} verified (NOT_SUPPORTED - Graceful fallback).")
                return True, result
            else:
                logger.warning(f"[WorkflowRuntime] ❌ Step {workflow.action} failed verification.")
                return False, result
                
        except Exception as e:
            logger.error(f"[WorkflowRuntime] Critical failure orchestrating step {workflow.action}: {str(e)}")
            return False, None
