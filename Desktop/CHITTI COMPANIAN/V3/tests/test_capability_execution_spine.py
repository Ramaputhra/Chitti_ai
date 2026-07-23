import os
import uuid
import datetime
from typing import Any, Dict, List
import json
import sys

from desktop.platform.shared.kernel.event_bus import InMemoryEventBus
from desktop.platform.integrations.core.capability_registry import RuntimeCapabilityRegistry
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.brain.runtimes.execution_runtime import ExecutionRuntime

from desktop.platform.shared.models.workflow import (
    Workflow, WorkflowStep, ExecutionPolicy, RetryPolicy, TimeoutClass
)
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor

from desktop.models.execution_events import (
    WorkflowCompletedEvent, TaskCompletedEvent, CapabilityInvokedEvent
)

from desktop.packages.desktop_pack.capabilities.time import TimeCapability
from desktop.packages.desktop_pack.capabilities.distance import DistanceCapability
from desktop.packages.desktop_pack.capabilities.navigation import NavigationCapability
from desktop.packages.desktop_pack.capabilities.browser import BrowserCapability
from desktop.packages.desktop_pack.capabilities.ocr import OCRCapability
from desktop.packages.desktop_pack.capabilities.search import SearchCapability

class VerboseLogger(ILoggingService):
    def info(self, msg: str) -> None: print(f"[INFO] {msg}")
    def error(self, msg: str) -> None: print(f"[ERROR] {msg}")
    def warning(self, msg: str) -> None: print(f"[WARN] {msg}")
    def debug(self, msg: str) -> None: print(f"[DEBUG] {msg}")
    def exception(self, msg: str, exc: Exception) -> None: print(f"[EXCEPTION] {msg}: {exc}")

class WorkflowTranslatorStub:
    def __init__(self, capability_id: str, tool_name: str, params: dict):
        self.capability_id = capability_id
        self.tool_name = tool_name
        self.params = params

    def translate(self) -> Workflow:
        policy = ExecutionPolicy(
            retry_policy=RetryPolicy(max_attempts=0, backoff_ms=0),
            timeout_class=TimeoutClass.INTERACTIVE
        )
        
        self.params["_tool_name"] = self.tool_name

        step = WorkflowStep(
            action="EXECUTE_CAPABILITY",
            step_id="step_1",
            parameters=self.params,
            policy=policy
        )
        return Workflow(
            steps=[step],
            workflow_id=f"wf_{uuid.uuid4()}",
        )

def run_verbose_integration():
    logger = VerboseLogger()
    event_bus = InMemoryEventBus()
    event_bus.initialize()
    
    registry = RuntimeCapabilityRegistry(logger)
    registry.initialize()
    
    caps = [
        TimeCapability(),
        DistanceCapability(),
        NavigationCapability(),
        BrowserCapability(),
        OCRCapability(),
        SearchCapability()
    ]
    
    print("\n==========================================================")
    print("RuntimeCapabilityRegistry Content Initialization")
    print("==========================================================")
    for cap in caps:
        registry.register_capability(cap)
        print(f"Registered Capability: {cap.name}")
        desc = cap.describe()
        print(f"Descriptor: name={desc.name}, version={desc.version}, tools={[t.name for t in desc.tools]}")
        
    execution_runtime = ExecutionRuntime(registry, event_bus)

    test_cases = [
        ("TimeCapability", "cap_time_query", "get_time", {}),
        ("DistanceCapability", "cap_distance_query", "get_distance", {"origin": "Home", "destination": "Work"}),
        ("NavigationCapability", "cap_live_navigation", "navigate", {"active_artifact": None}),
        ("BrowserCapability", "cap_browser_automation", "browser_action", {"action": "open", "url": "https://chitti.ai"}),
        ("OCRCapability", "cap_ocr_vision", "ocr_capture", {"source_window": "VSCode"}),
        ("SearchCapability", "cap_external_search", "search", {"query": "Latest AI models"})
    ]

    events = []
    def on_event(event):
        events.append(event.payload.get("event"))
        
    event_bus.subscribe_all(on_event)

    for class_name, cap_id, tool_name, params in test_cases:
        events.clear()
        
        print("\n==========================================================")
        print(f"Executing Scenario: {class_name}")
        print("==========================================================")
        
        print(f"[AIRuntime Resolution] Resolved Intent -> {tool_name}")
        print(f"[Planner Resolution] Mapped to capability_id: {class_name}")
        
        translator = WorkflowTranslatorStub(cap_id, tool_name, params)
        workflow = translator.translate()
        
        class DummyCapabilityReference:
            def __init__(self, cid):
                self.capability_id = cid
                self.version = "1.0"
        object.__setattr__(workflow.steps[0], 'capability', DummyCapabilityReference(class_name))
        
        class DummyParameterBinding:
            def __init__(self, k, v):
                self.parameter = k
                self.reference = v
        object.__setattr__(workflow.steps[0], 'parameter_bindings', [DummyParameterBinding(k, v) for k, v in params.items()])
        object.__setattr__(workflow, 'plan_id', "plan_123")
        
        try:
            print(f"[Registry Resolution] Resolving {class_name} from RuntimeCapabilityRegistry")
            cap = registry.get_capability(class_name)
            if cap:
                print(f"[Capability Descriptor] {cap.describe()}")
            else:
                print(f"[ERROR] Capability {class_name} not found in registry")
                continue
                
            print(f"[ExecutionRuntime Invocation] Executing Workflow {workflow.workflow_id}")
            execution_runtime.execute_workflow(workflow)
        except Exception as e:
            print(f"[Execution ERROR]: {e}")
            
        task_event = next((e for e in events if e.__class__.__name__ == "TaskCompletedEvent"), None)
        failed_event = next((e for e in events if e.__class__.__name__ == "TaskFailedEvent"), None)
        if task_event:
            output = task_event.output_data
            print(f"[ExecutionResult] status=SUCCESS")
            
            if "data" in output:
                canonical = output["data"]
                print(f"[VerificationRuntime Result] {canonical.verification_result}")
                print(f"[ConversationArtifact] {canonical.conversation_artifact}")
                print(f"[PresentationDescriptor] {canonical.presentation_descriptor}")
                print(f"[MemoryCandidate] {canonical.memory_candidate}")
            else:
                print(f"[Warning] 'data' key missing from TaskCompletedEvent output.")
                print(f"Raw Output: {output}")
        elif failed_event:
            print(f"[ExecutionResult] status=FAILED, error={failed_event.error_message}")
        else:
            print("[ERROR] No TaskCompletedEvent or TaskFailedEvent emitted.")

if __name__ == "__main__":
    run_verbose_integration()
