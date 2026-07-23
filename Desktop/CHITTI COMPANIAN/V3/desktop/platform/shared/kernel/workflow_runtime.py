import time
import threading
import uuid
from typing import Any, Optional

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.models.workflow import WorkflowState, Workflow, WorkflowContext, WorkflowStep

from desktop.platform.shared.kernel.cancellation import CancellationManager
from desktop.platform.shared.kernel.executor import WorkflowExecutor
from desktop.platform.shared.kernel.models import ExecutionContext
from desktop.platform.shared.kernel.persistence import PersistenceManager
from desktop.platform.shared.kernel.retry import RetryManager
from desktop.platform.shared.kernel.scheduler import WorkflowScheduler
from desktop.platform.shared.kernel.telemetry import TelemetryManager
from desktop.platform.shared.kernel.timeout import TimeoutManager


class WorkflowRuntime:
    """
    The Operating System for Execution.
    Rule 28: Kernel owns lifecycle transitions.
    Wraps the Executor and manages retries, timeout, telemetry, persistence, and scheduling.
    """
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        capability_invoker: Any = None, # Type Any to avoid circular imports if needed
        memory_api: Any = None,
    ) -> None:
        self._event_bus = event_bus
        self._logger = logger
        self._memory_api = memory_api
        
        # Subsystems
        self.telemetry = TelemetryManager(logger)
        self.persistence = PersistenceManager()
        self.cancellation = CancellationManager()
        self.timeout = TimeoutManager(self.cancellation)
        self.retry = RetryManager()
        self.scheduler = WorkflowScheduler()
        self.executor = WorkflowExecutor(capability_invoker=capability_invoker)
        
        self._pending_approvals: dict = {}
        self._approval_results: dict = {}

        self._running = False
        self._kernel_thread = threading.Thread(target=self._run_loop, daemon=True)

    @property
    def name(self) -> str:
        return "WorkflowRuntime"

    def initialize(self) -> None:
        self.telemetry.start()
        self._event_bus.subscribe(SystemEvents.WORKFLOW_CREATED, self._on_workflow_created)
        self._event_bus.subscribe(SystemEvents.WORKFLOW_APPROVAL_GRANTED, self._on_approval_granted)
        self._event_bus.subscribe(SystemEvents.WORKFLOW_APPROVAL_DENIED, self._on_approval_denied)
        self._running = True
        self._kernel_thread.start()
        self._logger.info("WorkflowRuntime initialized and started.")

    def _on_approval_granted(self, event: Event) -> None:
        approval_id = event.payload.get("approval_id")
        if approval_id in self._pending_approvals:
            self._approval_results[approval_id] = True
            self._pending_approvals[approval_id].set()
            
    def _on_approval_denied(self, event: Event) -> None:
        approval_id = event.payload.get("approval_id")
        if approval_id in self._pending_approvals:
            self._approval_results[approval_id] = False
            self._pending_approvals[approval_id].set()

    def shutdown(self) -> None:
        self._running = False
        if self._kernel_thread.is_alive():
            self._kernel_thread.join(timeout=2.0)
        self.telemetry.stop()
        self._logger.info("WorkflowRuntime shut down.")

    def _on_workflow_created(self, event: Event) -> None:
        """Only the WorkflowRuntime subscribes to Workflow.Created."""
        workflow = event.payload.get("workflow")
        task_id = event.payload.get("task_id")
        if workflow:
            # We inject task_id into metadata to carry it through ExecutionContext
            if task_id:
                workflow.metadata["task_id"] = task_id
            self.scheduler.enqueue(workflow)
            self.telemetry.emit("workflow_queued", {"workflow_id": workflow.workflow_id})
            self.persistence.record_event(workflow.workflow_id, WorkflowState.QUEUED)

    def _run_loop(self) -> None:
        """Background loop draining the scheduler queue."""
        while self._running:
            workflow = self.scheduler.next_ready()
            if workflow:
                self._execute_workflow(workflow)
            else:
                time.sleep(0.05) # Yield

    def _all_dependencies_completed(self, step: WorkflowStep, context: WorkflowContext) -> bool:
        """Checks if all prerequisite steps have completed successfully."""
        for dep in step.depends_on:
            if dep not in context.completed_steps:
                return False
        return True

    def _execute_workflow(self, workflow: Workflow) -> None:
        """
        Executes a workflow by orchestrating its steps.
        Linearly loops over steps, checking DAG dependencies (`depends_on`).
        """
        workflow.state = WorkflowState.RUNNING
        self.persistence.record_event(workflow.workflow_id, WorkflowState.RUNNING)
        self.telemetry.emit("workflow_started", {"workflow_id": workflow.workflow_id})
        
        self._event_bus.publish(Event(
            SystemEvents.WORKFLOW_STARTED,
            self.name,
            {"workflow_id": workflow.workflow_id, "task_id": workflow.metadata.get("task_id")}
        ))
        
        task_id = workflow.metadata.get("task_id")
        
        # Create Orchestration Context
        workflow_context = WorkflowContext(
            workflow_id=workflow.workflow_id,
            task_id=task_id,
        )

        # Create immutable ExecutionContext
        exec_context = ExecutionContext(
            session_id=str(uuid.uuid4()),      # Temp for sprint 14
            conversation_id=str(uuid.uuid4()), # Temp for sprint 14
            workflow_id=workflow.workflow_id,
            step_id="",                        # Updated per step
            capability_runtime=None,           # Injected later
            memory_runtime=self._memory_api,
            inference_runtime=None,            # Injected later
            expression_runtime=None,           # Injected later
            telemetry_manager=self.telemetry
        )

        # Linear traversal of topologically ordered steps
        for step in workflow.steps:
            if step.step_id in workflow_context.completed_steps:
                continue

            if not self._all_dependencies_completed(step, workflow_context):
                self._logger.error(f"Dependencies not met for step {step.step_id}. Halting workflow.")
                self._rollback_workflow(workflow, workflow_context)
                return

            workflow_context.current_step = step.step_id
            
            # Use object.__setattr__ to bypass frozen dataclass just for step_id injection
            object.__setattr__(exec_context, "step_id", step.step_id)

            success = self._execute_step(workflow, step, exec_context)
            
            if success:
                workflow_context.completed_steps.append(step.step_id)
            else:
                workflow_context.failed_steps.append(step.step_id)
                # Check for branching to on_failure
                if step.on_failure:
                    failure_step = next((s for s in workflow.steps if s.step_id == step.on_failure), None)
                    if failure_step:
                        self._logger.info(f"Step {step.step_id} failed. Executing on_failure step {failure_step.step_id}.")
                        object.__setattr__(exec_context, "step_id", failure_step.step_id)
                        self._execute_step(workflow, failure_step, exec_context)
                
                self._rollback_workflow(workflow, workflow_context)
                return

        self._mark_workflow_completed(workflow, workflow_context)

    def _execute_step(self, workflow: Workflow, step: WorkflowStep, context: ExecutionContext) -> bool:
        """
        Executes a single step, handling approvals, timeouts, retries, and cancellation.
        """
        step_id = step.step_id
        token = self.cancellation.create_token(workflow.workflow_id)
        
        self._event_bus.publish(Event(
            SystemEvents.STEP_STARTED,
            self.name,
            {"workflow_id": workflow.workflow_id, "step_id": step_id, "action": step.action}
        ))
        
        if step.policy.timeout_ms:
            self.timeout.schedule_timeout(workflow.workflow_id, step_id, step.policy.timeout_ms)
        else:
            self.timeout.schedule_timeout(workflow.workflow_id, step_id, step.policy.timeout_class.value)

        if step.policy.requires_approval:
            self._logger.info(f"Workflow {workflow.workflow_id} requires approval for step {step_id}")
            approval_id = str(uuid.uuid4())
            approval_event = threading.Event()
            self._pending_approvals[approval_id] = approval_event
            
            self._event_bus.publish(Event(
                SystemEvents.WORKFLOW_APPROVAL_REQUIRED,
                self.name,
                {
                    "workflow_id": workflow.workflow_id,
                    "step_id": step_id,
                    "approval_id": approval_id,
                    "prompt": getattr(step.policy, 'approval_prompt', None) or "Approval required."
                }
            ))
            
            approval_event.wait(timeout=300.0)
            granted = self._approval_results.get(approval_id, False)
            
            self._pending_approvals.pop(approval_id, None)
            self._approval_results.pop(approval_id, None)
            
            if not granted:
                self._logger.info(f"Workflow {workflow.workflow_id} approval denied.")
                return False

        step_success = False
        while self.retry.should_retry(workflow.workflow_id, step_id, step.policy) and not step_success:
            if token.cancelled:
                return False
            
            start_time = time.time()
            result = self.executor.execute(step, context, token)
            duration = int((time.time() - start_time) * 1000)

            self.persistence.record_step_result(workflow.workflow_id, step_id, result)
            self.telemetry.emit("step_executed", {
                "workflow_id": workflow.workflow_id,
                "action": step.action,
                "duration_ms": duration,
                "success": result.success
            })

            if result.success:
                step_success = True
                self._event_bus.publish(Event(
                    SystemEvents.STEP_COMPLETED,
                    self.name,
                    {"workflow_id": workflow.workflow_id, "step_id": step_id, "action": step.action, "result": result.output}
                ))
                # Legacy event for backward-compat during migration
                self._event_bus.publish(Event(
                    SystemEvents.WORKFLOW_STEP_COMPLETED,
                    self.name,
                    {"workflow_id": workflow.workflow_id, "step_action": step.action}
                ))
            else:
                if token.cancelled:
                    return False
                    
                self.persistence.record_event(workflow.workflow_id, WorkflowState.RETRYING)
                self.retry.record_failure_and_wait(workflow.workflow_id, step_id)

        self.timeout.cancel_timeout(workflow.workflow_id, step_id)
        
        if not step_success:
            self._event_bus.publish(Event(
                SystemEvents.STEP_FAILED,
                self.name,
                {"workflow_id": workflow.workflow_id, "step_id": step_id, "action": step.action, "error": "Step failed after retries."}
            ))

        return step_success

    def _rollback_workflow(self, workflow: Workflow, context: WorkflowContext) -> None:
        self._logger.info(f"Rolling back workflow {workflow.workflow_id}")
        
        # Execute compensation steps in reverse order
        for step_id in reversed(context.completed_steps):
            step = next((s for s in workflow.steps if s.step_id == step_id), None)
            if step and step.compensation_step_id:
                comp_step = next((s for s in workflow.steps if s.step_id == step.compensation_step_id), None)
                if comp_step:
                    self._logger.info(f"Executing compensation {comp_step.step_id} for step {step.step_id}")
                    # Recreate context for compensation step
                    exec_context = ExecutionContext(
                        session_id=str(uuid.uuid4()),
                        conversation_id=str(uuid.uuid4()),
                        workflow_id=workflow.workflow_id,
                        step_id=comp_step.step_id,
                        capability_runtime=None,
                        memory_runtime=self._memory_api,
                        inference_runtime=None,
                        expression_runtime=None,
                        telemetry_manager=self.telemetry
                    )
                    self._execute_step(workflow, comp_step, exec_context)

        self._mark_workflow_rolled_back(workflow, context)

    def _mark_workflow_completed(self, workflow: Workflow, context: WorkflowContext) -> None:
        workflow.state = WorkflowState.COMPLETED
        self.persistence.record_event(workflow.workflow_id, WorkflowState.COMPLETED)
        self.telemetry.emit("workflow_completed", {"workflow_id": workflow.workflow_id})
        
        self._event_bus.publish(Event(
            SystemEvents.WORKFLOW_COMPLETED,
            self.name,
            {"workflow_id": workflow.workflow_id, "task_id": context.task_id}
        ))
        
        self._cleanup(workflow.workflow_id)

    def _mark_workflow_rolled_back(self, workflow: Workflow, context: WorkflowContext) -> None:
        workflow.state = WorkflowState.FAILED
        self.persistence.record_event(workflow.workflow_id, WorkflowState.FAILED)
        self.telemetry.emit("workflow_failed", {"workflow_id": workflow.workflow_id})
        
        self._event_bus.publish(Event(
            SystemEvents.WORKFLOW_ROLLED_BACK,
            self.name,
            {"workflow_id": workflow.workflow_id, "task_id": context.task_id}
        ))
        
        self._cleanup(workflow.workflow_id)
        
    def _mark_workflow_cancelled(self, workflow: Workflow) -> None:
        workflow.state = WorkflowState.CANCELLED
        self.persistence.record_event(workflow.workflow_id, WorkflowState.CANCELLED)
        self.telemetry.emit("workflow_cancelled", {"workflow_id": workflow.workflow_id})
        self._cleanup(workflow.workflow_id)
        
    def _cleanup(self, workflow_id: str) -> None:
        self.cancellation.cleanup_token(workflow_id)
        self.timeout.cleanup_workflow(workflow_id)
        self.retry.cleanup_workflow(workflow_id)
