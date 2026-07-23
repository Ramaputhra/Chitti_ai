import asyncio
import time
import logging
from typing import Any
from desktop.platform.shared.models.workflow import Workflow, WorkflowState, WorkflowStep, TimeoutClass
from desktop.runtimes.workflow.context import WorkflowContext
from desktop.runtimes.workflow.models import ExecutionResult, ExecutionStatus, StepExecutionRecord
from desktop.runtimes.workflow.policies import RetryManager
from desktop.runtimes.workflow.events import (
    WorkflowStarted, WorkflowCompleted, WorkflowFailed, WorkflowCancelled,
    StepStarted, StepCompleted, StepFailed
)
from desktop.runtimes.capability.runtime import CapabilityRuntime

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    """
    Responsible for executing a single Workflow, strictly managing state transitions, 
    timeouts, retries, and cancellation (Rule 24, 25, 41).
    """
    def __init__(self, workflow: Workflow, event_bus: Any, capability_runtime: CapabilityRuntime):
        self.workflow = workflow
        self.event_bus = event_bus
        self.capability_runtime = capability_runtime
        self.context = WorkflowContext(
            workflow_id=workflow.workflow_id,
            execution_id=str(time.time())
        )
        self._state = WorkflowState.CREATED

    def _transition(self, new_state: WorkflowState):
        """State machine for single workflow execution."""
        logger.debug(f"[Workflow {self.workflow.workflow_id}] {self._state.name} -> {new_state.name}")
        self._state = new_state

    async def execute(self) -> ExecutionResult:
        """Executes the workflow sequentially."""
        self._transition(WorkflowState.READY)
        self._transition(WorkflowState.RUNNING)
        
        if hasattr(self.event_bus, "publish"):
            self.event_bus.publish(WorkflowStarted(self.workflow.workflow_id, self.workflow.source_intent))

        for step in self.workflow.steps:
            if self.context.cancellation_token.is_cancelled:
                self._transition(WorkflowState.CANCELLED)
                if hasattr(self.event_bus, "publish"):
                    self.event_bus.publish(WorkflowCancelled(self.workflow.workflow_id))
                return ExecutionResult(status=ExecutionStatus.CANCELLED)

            self.context.current_step = step.step_id
            
            # Idempotency check (Rule 25)
            # If we've already successfully completed this step in a previous attempt, skip it.
            # (Normally applies if we were resuming from a checkpoint, but we just check memory here)
            if step.step_id in self.context.variables.get("completed_steps", []):
                continue

            if hasattr(self.event_bus, "publish"):
                self.event_bus.publish(StepStarted(self.workflow.workflow_id, step.step_id, step.action))

            result = await self._execute_step_with_policies(step)
            
            if result.status == ExecutionStatus.SUCCESS:
                if hasattr(self.event_bus, "publish"):
                    self.event_bus.publish(StepCompleted(self.workflow.workflow_id, step.step_id, step.action, result.output or {}))
                
                # Update context
                completed = self.context.variables.setdefault("completed_steps", [])
                completed.append(step.step_id)
                self.context.variables.update(result.metadata.get("exports", {}))
                
            elif result.status == ExecutionStatus.CANCELLED:
                self._transition(WorkflowState.CANCELLED)
                if hasattr(self.event_bus, "publish"):
                    self.event_bus.publish(WorkflowCancelled(self.workflow.workflow_id))
                return result
                
            else:
                self._transition(WorkflowState.FAILED)
                if hasattr(self.event_bus, "publish"):
                    self.event_bus.publish(StepFailed(self.workflow.workflow_id, step.step_id, step.action, result.error_message or "Unknown Error"))
                    self.event_bus.publish(WorkflowFailed(self.workflow.workflow_id, result.error_message or "Workflow Step Failed"))
                return result

        self._transition(WorkflowState.COMPLETED)
        if hasattr(self.event_bus, "publish"):
            self.event_bus.publish(WorkflowCompleted(self.workflow.workflow_id))
            
        return ExecutionResult(status=ExecutionStatus.SUCCESS)

    async def _execute_step_with_policies(self, step: WorkflowStep) -> ExecutionResult:
        """Applies retry and timeout policies to the raw capability invocation."""
        timeout_ms = step.policy.timeout_ms
        if timeout_ms is None:
            timeout_ms = step.policy.timeout_class.value if step.policy.timeout_class else TimeoutClass.INTERACTIVE.value

        async def _attempt():
            start_time = time.time()
            try:
                # Enforce timeout cooperative wrapping
                # Note: asyncio.wait_for will cancel the inner task if it times out
                result = await asyncio.wait_for(
                    self._invoke_capability(step),
                    timeout=timeout_ms / 1000.0
                )
            except asyncio.TimeoutError:
                self.context.cancellation_token.cancel() # Signal capability to stop
                result = ExecutionResult(status=ExecutionStatus.FAILURE, error_message=f"Timeout after {timeout_ms}ms")
            except Exception as e:
                result = ExecutionResult(status=ExecutionStatus.FAILURE, error_message=str(e))
                
            record = StepExecutionRecord(
                step_id=step.step_id,
                attempt=1, # Managed by RetryManager context theoretically
                status=result.status,
                started_at=start_time,
                finished_at=time.time(),
                result=result
            )
            self.context.add_record(record)
            return result

        return await RetryManager.execute_with_retry(step.policy.retry_policy, _attempt)

    async def _invoke_capability(self, step: WorkflowStep) -> ExecutionResult:
        """
        The Capability RPC. (Rule 42)
        Translates a WorkflowStep into a capability execution.
        """
        action = step.action
        params = step.parameters

        cap_id = params.get("capability_id", action)
        
        return await self.capability_runtime.invoke(
            capability_id=cap_id,
            parameters=params,
            execution_context=self.context,
            cancellation_token=self.context.cancellation_token
        )

    def cancel(self):
        """External request to cancel workflow execution."""
        logger.info(f"Cancelling workflow {self.workflow.workflow_id}")
        self.context.cancellation_token.cancel()
