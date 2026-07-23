import asyncio
from typing import Any, Dict, List
from datetime import datetime

from desktop.platform.shared.kernel.event_bus import InMemoryEventBus
from desktop.platform.integrations.core.capability_registry import RuntimeCapabilityRegistry
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.brain.runtimes.execution_runtime import ExecutionRuntime
from desktop.models.workflow import (
    Workflow, WorkflowStep, CapabilityReference, 
    ExecutionPolicy, RetryPolicy, TimeoutPolicy, FallbackPolicy,
    WorkflowMetadata
)
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor

class MockLogger(ILoggingService):
    def info(self, msg: str) -> None: print(f"INFO: {msg}")
    def error(self, msg: str) -> None: print(f"ERROR: {msg}")
    def warning(self, msg: str) -> None: print(f"WARNING: {msg}")
    def debug(self, msg: str) -> None: print(f"DEBUG: {msg}")
    def exception(self, msg: str, exc: Exception) -> None: print(f"EXC: {msg} {exc}")

class MockCapability(ICapability):
    @property
    def name(self) -> str: return "MockCapability"
    @property
    def state(self) -> Any: return None
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[ToolDescriptor]: return []
    def validate(self, invocation: ToolInvocation) -> bool: return True
    def cancel(self, invocation_id: str) -> None: pass
    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(name="MockCapability", description="A mock capability", version="1.0", tools=[])
        
    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        return ExecutionResult(status=ExecutionStatus.SUCCESS, summary="Mock execution successful")


def test_sprint_108():
    logger = MockLogger()
    event_bus = InMemoryEventBus()
    event_bus.initialize()
    
    registry = RuntimeCapabilityRegistry(logger)
    registry.initialize()
    registry.register_capability(MockCapability())
    
    runtime = ExecutionRuntime(registry, event_bus)
    
    policy = ExecutionPolicy(
        retry=RetryPolicy(max_retries=0, retry_backoff_ms=0),
        timeout=TimeoutPolicy(timeout_ms=1000),
        fallback=FallbackPolicy(fallback_workflow_id=None)
    )
    
    step = WorkflowStep(
        step_id="step_1",
        capability=CapabilityReference(capability_id="MockCapability", version="1.0"),
        parameter_bindings=[],
        execution_policy=policy
    )
    
    workflow = Workflow(
        workflow_id="wf_001",
        plan_id="plan_001",
        steps=[step],
        transitions=[],
        global_policy=policy,
        metadata=WorkflowMetadata(translator_version="1.0", created_at=datetime.utcnow(), generated_from_plan_id="plan_001")
    )
    
    # Subscribe to events to collect them
    recorded_events = []
    def on_event(event):
        recorded_events.append(event.payload.get("event"))
    
    event_bus.subscribe_all(on_event)
    
    # First execution
    runtime.execute_workflow(workflow)
    
    first_execution_classes = [e.__class__.__name__ for e in recorded_events]
    
    # Second execution
    recorded_events.clear()
    runtime.execute_workflow(workflow)
    
    second_execution_classes = [e.__class__.__name__ for e in recorded_events]
    
    print("First execution event sequence:", first_execution_classes)
    print("Second execution event sequence:", second_execution_classes)
    
    assert first_execution_classes == second_execution_classes, "Executions are not identical!"
    assert first_execution_classes == [
        "WorkflowStartedEvent",
        "TaskStartedEvent",
        "CapabilityInvokedEvent",
        "TaskCompletedEvent",
        "WorkflowCompletedEvent"
    ], "Event sequence does not match expected Definition of Done."
    
    print("Sprint 108 Definition of Done: PASS")

if __name__ == "__main__":
    test_sprint_108()
