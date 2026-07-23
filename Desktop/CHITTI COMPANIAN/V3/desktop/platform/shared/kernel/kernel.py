import time
import threading
import uuid
from typing import Any

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.models.workflow import WorkflowState

from desktop.platform.shared.kernel.cancellation import CancellationManager
from desktop.platform.shared.kernel.executor import WorkflowExecutor
from desktop.platform.shared.kernel.models import ExecutionContext
from desktop.platform.shared.kernel.persistence import PersistenceManager
from desktop.platform.shared.kernel.retry import RetryManager
from desktop.platform.shared.kernel.scheduler import WorkflowScheduler
from desktop.platform.shared.kernel.telemetry import TelemetryManager
from desktop.platform.shared.kernel.timeout import TimeoutManager


class RuntimeKernel:
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

    def initialize(self) -> None:
        self.telemetry.start()
        self._event_bus.subscribe(SystemEvents.WORKFLOW_CREATED, self._on_workflow_created)
        self._event_bus.subscribe(SystemEvents.WORKFLOW_APPROVAL_GRANTED, self._on_approval_granted)
        self._event_bus.subscribe(SystemEvents.WORKFLOW_APPROVAL_DENIED, self._on_approval_denied)
        self._running = True
        self._kernel_thread.start()
        self._logger.info("RuntimeKernel initialized and started.")

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
        self._logger.info("RuntimeKernel shut down.")

    def _on_workflow_created(self, event: Event) -> None:
        """Only the Kernel subscribes to Workflow.Created (Rule 28)."""
        workflow = event.payload.get("workflow")
        if workflow:
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

    def _execute_workflow(self, workflow: Any) -> None:
        """Executes a workflow by orchestrating its steps and handling lifecycle constraints."""
        workflow.state = WorkflowState.RUNNING
        self.persistence.record_event(workflow.workflow_id, WorkflowState.RUNNING)
        self.telemetry.emit("workflow_started", {"workflow_id": workflow.workflow_id})
        
        # Create immutable ExecutionContext
        context = ExecutionContext(
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

        for step in workflow.steps:
            step_id = f"{workflow.workflow_id}_{hash(step)}"
            # Recreate context with current step_id (using object.__setattr__ since it's frozen, or just replace it)
            # For simplicity, we just pass step_id through step iteration
            
            token = self.cancellation.create_token(workflow.workflow_id)
            
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
                    "RuntimeKernel",
                    {
                        "workflow_id": workflow.workflow_id,
                        "step_id": step_id,
                        "approval_id": approval_id,
                        "prompt": getattr(step.policy, 'approval_prompt', None) or "Approval required."
                    }
                ))
                
                # Block until approval is granted or denied (or timeout)
                approval_event.wait(timeout=300.0) # 5 min timeout for approval
                granted = self._approval_results.get(approval_id, False)
                
                # Cleanup
                self._pending_approvals.pop(approval_id, None)
                self._approval_results.pop(approval_id, None)
                
                if not granted:
                    self._logger.info(f"Workflow {workflow.workflow_id} approval denied.")
                    self._mark_workflow_cancelled(workflow)
                    return

            step_success = False
            while self.retry.should_retry(workflow.workflow_id, step_id, step.policy) and not step_success:
                
                # Check cancellation prior to execution
                if token.cancelled:
                    self._mark_workflow_cancelled(workflow)
                    return
                
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
                else:
                    if token.cancelled:
                        self._mark_workflow_cancelled(workflow)
                        return
                        
                    self.persistence.record_event(workflow.workflow_id, WorkflowState.RETRYING)
                    self.retry.record_failure_and_wait(workflow.workflow_id, step_id)

            self.timeout.cancel_timeout(workflow.workflow_id, step_id)

            if not step_success:
                self._mark_workflow_failed(workflow)
                return

        self._mark_workflow_completed(workflow)

    def _mark_workflow_completed(self, workflow: Any) -> None:
        workflow.state = WorkflowState.COMPLETED
        self.persistence.record_event(workflow.workflow_id, WorkflowState.COMPLETED)
        self.telemetry.emit("workflow_completed", {"workflow_id": workflow.workflow_id})
        self._cleanup(workflow.workflow_id)

    def _mark_workflow_failed(self, workflow: Any) -> None:
        workflow.state = WorkflowState.FAILED
        self.persistence.record_event(workflow.workflow_id, WorkflowState.FAILED)
        self.telemetry.emit("workflow_failed", {"workflow_id": workflow.workflow_id})
        self._cleanup(workflow.workflow_id)
        
    def _mark_workflow_cancelled(self, workflow: Any) -> None:
        workflow.state = WorkflowState.CANCELLED
        self.persistence.record_event(workflow.workflow_id, WorkflowState.CANCELLED)
        self.telemetry.emit("workflow_cancelled", {"workflow_id": workflow.workflow_id})
        self._cleanup(workflow.workflow_id)
        
    def _cleanup(self, workflow_id: str) -> None:
        self.cancellation.cleanup_token(workflow_id)
        self.timeout.cleanup_workflow(workflow_id)
        self.retry.cleanup_workflow(workflow_id)
