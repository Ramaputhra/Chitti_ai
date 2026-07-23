import time
import uuid
from typing import Dict, Any
from dataclasses import dataclass, field

from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.interfaces.capability_registry import IRuntimeCapabilityRegistry
from desktop.platform.shared.models.workflow import Workflow, WorkflowState as WorkflowStatus

@dataclass
class WorkflowExecution:
    workflow_id: str
    status: WorkflowStatus
    started_at: Any
    completed_at: Any
    current_step_id: Any
    last_completed_step_id: Any
    error_details: Any
from desktop.models.execution_events import (
    WorkflowStartedEvent,
    WorkflowCompletedEvent,
    TaskStartedEvent,
    CapabilityInvokedEvent,
    TaskCompletedEvent,
    TaskFailedEvent
)
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionTelemetry, ExecutionStatus


@dataclass
class RuntimeExecutionContext:
    """Runtime state for a single workflow execution."""
    workflow_execution: WorkflowExecution
    event_bus: IEventBus
    capability_registry: IRuntimeCapabilityRegistry
    outputs: Dict[str, Any] = field(default_factory=dict)


class ExecutionRuntime:
    """
    The foundational runtime for physical execution.
    Consumes a Workflow, executes capabilities, and emits immutable ExecutionEvents.
    """
    def __init__(self, capability_registry: IRuntimeCapabilityRegistry, event_bus: IEventBus):
        self.registry = capability_registry
        self.event_bus = event_bus

    def execute_workflow(self, workflow: Workflow) -> None:
        """Executes a Workflow synchronously (Sprint 108 slice)."""
        correlation_id = str(uuid.uuid4())
        
        # Initialize runtime context
        wf_execution = WorkflowExecution(
            workflow_id=workflow.workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=__import__('datetime').datetime.utcnow(),
            completed_at=None,
            current_step_id=None,
            last_completed_step_id=None,
            error_details=None
        )
        
        runtime_context = RuntimeExecutionContext(
            workflow_execution=wf_execution,
            event_bus=self.event_bus,
            capability_registry=self.registry
        )
        
        # 1. Emit WorkflowStartedEvent
        wf_start_event = WorkflowStartedEvent(
            event_id=str(uuid.uuid4()),
            workflow_id=workflow.workflow_id,
            plan_id=workflow.plan_id,
            correlation_id=correlation_id,
            sequence_number=1,
            timestamp=__import__('datetime').datetime.utcnow()
        )
        self.event_bus.publish(Event(event_id=wf_start_event.event_id, source="ExecutionRuntime", payload={"event": wf_start_event}))
        
        seq_num = 2
        
        # 2. Iterate sequentially over workflow.steps
        import dataclasses
        for step in workflow.steps:
            runtime_context.workflow_execution = dataclasses.replace(
                runtime_context.workflow_execution, current_step_id=step.step_id
            )
            
            # Emit TaskStartedEvent
            task_start = TaskStartedEvent(
                event_id=str(uuid.uuid4()),
                workflow_id=workflow.workflow_id,
                plan_id=workflow.plan_id,
                correlation_id=correlation_id,
                sequence_number=seq_num,
                timestamp=__import__('datetime').datetime.utcnow(),
                task_id=step.step_id,
                capability_id=step.capability.capability_id
            )
            self.event_bus.publish(Event(event_id=task_start.event_id, source="ExecutionRuntime", payload={"event": task_start}))
            seq_num += 1
            
            # Lookup capability
            capability = self.registry.get_capability(step.capability.capability_id)
            if not capability:
                task_failed = TaskFailedEvent(
                    event_id=str(uuid.uuid4()),
                    workflow_id=workflow.workflow_id,
                    plan_id=workflow.plan_id,
                    correlation_id=correlation_id,
                    sequence_number=seq_num,
                    timestamp=__import__('datetime').datetime.utcnow(),
                    task_id=step.step_id,
                    capability_id=step.capability.capability_id,
                    error_code="CAPABILITY_NOT_FOUND",
                    error_message=f"Capability {step.capability.capability_id} not found in registry.",
                    retry_count=0
                )
                self.event_bus.publish(Event(event_id=task_failed.event_id, source="ExecutionRuntime", payload={"event": task_failed}))
                return # Fast fail for Sprint 108

            # Resolve parameters (Sprint 108: literal pass-through)
            resolved_args = {b.parameter: b.reference for b in step.parameter_bindings}
            
            # Emit CapabilityInvokedEvent
            invocation_id = str(uuid.uuid4())
            cap_invoked = CapabilityInvokedEvent(
                event_id=str(uuid.uuid4()),
                workflow_id=workflow.workflow_id,
                plan_id=workflow.plan_id,
                correlation_id=correlation_id,
                sequence_number=seq_num,
                timestamp=__import__('datetime').datetime.utcnow(),
                task_id=step.step_id,
                capability_id=step.capability.capability_id,
                version=step.capability.version,
                input_parameters=resolved_args,
                invocation_id=invocation_id
            )
            self.event_bus.publish(Event(event_id=cap_invoked.event_id, source="ExecutionRuntime", payload={"event": cap_invoked}))
            seq_num += 1

            # Invoke capability
            start_time = time.time()
            
            # Create dummy invocation
            invocation = ToolInvocation(
                id=invocation_id,
                tool_name=resolved_args.get("_tool_name", step.capability.capability_id),
                arguments=resolved_args,
                confidence=1.0,
                source="ExecutionRuntime"
            )
            
            # Create dummy core context for the capability itself
            telemetry = ExecutionTelemetry(capability=step.capability.capability_id, tool=step.capability.capability_id, status="RUNNING")
            cap_context = ExecutionContext(
                session=None, # type: ignore
                user="system",
                permissions=[],
                timeout_sec=30.0,
                cancellation_token=None,
                telemetry=telemetry
            )
            
            try:
                result = capability.execute(invocation, cap_context)
                duration_ms = (time.time() - start_time) * 1000
                
                if result.status == ExecutionStatus.SUCCESS:
                    # Store output in runtime context, preserving full canonical payload
                    runtime_context.outputs[step.step_id] = {
                        "summary": result.summary,
                        "data": result.data,
                        "status": result.status.name
                    }
                    
                    task_completed = TaskCompletedEvent(
                        event_id=str(uuid.uuid4()),
                        workflow_id=workflow.workflow_id,
                        plan_id=workflow.plan_id,
                        correlation_id=correlation_id,
                        sequence_number=seq_num,
                        timestamp=__import__('datetime').datetime.utcnow(),
                        task_id=step.step_id,
                        capability_id=step.capability.capability_id,
                        output_data=runtime_context.outputs[step.step_id],
                        duration_ms=duration_ms
                    )
                    self.event_bus.publish(Event(event_id=task_completed.event_id, source="ExecutionRuntime", payload={"event": task_completed}))
                    runtime_context.workflow_execution = dataclasses.replace(
                        runtime_context.workflow_execution, last_completed_step_id=step.step_id
                    )
                else:
                    task_failed = TaskFailedEvent(
                        event_id=str(uuid.uuid4()),
                        workflow_id=workflow.workflow_id,
                        plan_id=workflow.plan_id,
                        correlation_id=correlation_id,
                        sequence_number=seq_num,
                        timestamp=__import__('datetime').datetime.utcnow(),
                        task_id=step.step_id,
                        capability_id=step.capability.capability_id,
                        error_code="EXECUTION_FAILED",
                        error_message=result.summary,
                        retry_count=0
                    )
                    self.event_bus.publish(Event(event_id=task_failed.event_id, source="ExecutionRuntime", payload={"event": task_failed}))
                    return
            except Exception as e:
                task_failed = TaskFailedEvent(
                    event_id=str(uuid.uuid4()),
                    workflow_id=workflow.workflow_id,
                    plan_id=workflow.plan_id,
                    correlation_id=correlation_id,
                    sequence_number=seq_num,
                    timestamp=__import__('datetime').datetime.utcnow(),
                    task_id=step.step_id,
                    capability_id=step.capability.capability_id,
                    error_code="UNHANDLED_EXCEPTION",
                    error_message=str(e),
                    retry_count=0
                )
                self.event_bus.publish(Event(event_id=task_failed.event_id, source="ExecutionRuntime", payload={"event": task_failed}))
                return
            
            seq_num += 1

        # 4. Emit WorkflowCompletedEvent
        wf_completed = WorkflowCompletedEvent(
            event_id=str(uuid.uuid4()),
            workflow_id=workflow.workflow_id,
            plan_id=workflow.plan_id,
            correlation_id=correlation_id,
            sequence_number=seq_num,
            timestamp=__import__('datetime').datetime.utcnow(),
            duration_ms=0.0 # TODO: track total duration
        )
        self.event_bus.publish(Event(event_id=wf_completed.event_id, source="ExecutionRuntime", payload={"event": wf_completed}))
