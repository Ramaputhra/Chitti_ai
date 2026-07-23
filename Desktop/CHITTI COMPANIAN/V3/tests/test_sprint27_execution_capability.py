import uuid
import datetime
from typing import Any, Dict, List

from desktop.platform.shared.kernel.event_bus import InMemoryEventBus
from desktop.platform.integrations.core.capability_registry import RuntimeCapabilityRegistry
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.brain.runtimes.execution_runtime import ExecutionRuntime
from desktop.models.capability import CanonicalCapabilityOutput

from desktop.packages.desktop_pack.capabilities.application import LaunchApplicationCapability
from desktop.packages.desktop_pack.capabilities.workspace_state import WorkspaceStateCapability
from desktop.packages.desktop_pack.capabilities.workspace import FileOpenCapability, WorkingDirectoryCapability
from desktop.models.execution_plan import ExecutionPlan, ExecutionPlanNode, ExecutionDelta

class VerboseLogger(ILoggingService):
    def info(self, msg: str) -> None: print(f"[INFO] {msg}")
    def error(self, msg: str) -> None: print(f"[ERROR] {msg}")
    def warning(self, msg: str) -> None: print(f"[WARN] {msg}")
    def debug(self, msg: str) -> None: print(f"[DEBUG] {msg}")
    def exception(self, msg: str, exc: Exception) -> None: print(f"[EXCEPTION] {msg}: {exc}")

class MockConversationRuntime:
    def __init__(self, event_bus: InMemoryEventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe_all(self._on_event)

    def _on_event(self, event: Any):
        # We simulate EventBus listening for Capability events for Narration
        # Because we're just printing out mock strings, we'll intercept here
        if isinstance(event, dict) and "action" in event:
            if event["action"] == "capability_started":
                if "app" in event: print(f"[ConversationRuntime] Narration: 'Opening {event['app']}...'")
                elif "dir" in event: print(f"[ConversationRuntime] Narration: 'Opening your AI project...'")
                elif "file" in event: print(f"[ConversationRuntime] Narration: 'Opening file {event['file']}...'")
            elif event["action"] == "capability_completed":
                if "app" in event and not event.get("success"):
                    print(f"[ConversationRuntime] Narration: '{event['app']} could not be restored because the executable was not found.'")

class MockVerificationRuntime:
    def evaluate(self, plan: ExecutionPlan, outputs: List[CanonicalCapabilityOutput]) -> ExecutionDelta:
        expected = ["Cursor", "PowerShell", "Chrome", "/home/user/projects/ai_development", "main.py"]
        observed = ["Cursor", "Chrome", "/home/user/projects/ai_development", "main.py"]
        failed = ["PowerShell"]
        skipped = []
        missing = []
        
        delta = ExecutionDelta(
            expected=expected,
            observed=observed,
            missing=missing,
            failed=failed,
            skipped=skipped
        )
        print("\n==========================================================")
        print("[VerificationRuntime] Generating ExecutionDelta")
        print(f"Expected: {expected}")
        print(f"Observed: {observed}")
        print(f"Failed: {failed}")
        print("==========================================================")
        return delta

class MockPresentationRuntime:
    def render_progress(self, current_node: str, completed: int, total: int):
        print(f"[PresentationRuntime] UI Update: Progress {completed}/{total} | Current: {current_node}")
        
    def render_final(self, delta: ExecutionDelta):
        print(f"[PresentationRuntime] Final UI Dashboard updated with ExecutionDelta (Observed: {len(delta.observed)}, Failed: {len(delta.failed)})")

class MockPlannerRuntime:
    def build_plan(self) -> ExecutionPlan:
        node1 = ExecutionPlanNode("n1", "WorkingDirectoryCapability", "set_working_directory", {"directory": "/home/user/projects/ai_development"})
        node2 = ExecutionPlanNode("n2", "LaunchApplicationCapability", "launch_application", {"app_name": "Cursor"}, dependencies=["n1"])
        node3 = ExecutionPlanNode("n3", "LaunchApplicationCapability", "launch_application", {"app_name": "PowerShell"}, dependencies=["n1"])
        node4 = ExecutionPlanNode("n4", "LaunchApplicationCapability", "launch_application", {"app_name": "Chrome"}, dependencies=["n1"])
        node5 = ExecutionPlanNode("n5", "FileOpenCapability", "open_file", {"file_path": "main.py"}, dependencies=["n2"])
        
        print("\n==========================================================")
        print("[PlannerRuntime] Built ExecutionPlan dependency graph.")
        print("==========================================================")
        return ExecutionPlan(plan_id="plan_1", nodes=[node1, node2, node3, node4, node5])

def run_sprint27_execution():
    logger = VerboseLogger()
    event_bus = InMemoryEventBus()
    event_bus.initialize()
    
    registry = RuntimeCapabilityRegistry(logger)
    registry.initialize()
    
    registry.register_capability(LaunchApplicationCapability())
    registry.register_capability(WorkspaceStateCapability())
    registry.register_capability(FileOpenCapability())
    registry.register_capability(WorkingDirectoryCapability())
    
    execution_runtime = ExecutionRuntime(registry, event_bus)
    planner = MockPlannerRuntime()
    conversation = MockConversationRuntime(event_bus)
    verification = MockVerificationRuntime()
    presentation = MockPresentationRuntime()
    
    # 1. Planner builds graph
    plan = planner.build_plan()
    
    outputs = []
    completed_count = 0
    total = len(plan.nodes)
    
    from desktop.platform.shared.models.ai import ToolInvocation
    
    print("\n==========================================================")
    print("[ExecutionRuntime] Traversing ExecutionPlan nodes (simulating dependency resolution)")
    print("==========================================================")
    
    # 2. ExecutionRuntime executes the graph safely
    for node in plan.nodes:
        presentation.render_progress(node.tool_name, completed_count, total)
        
        cap = registry.get_capability(node.capability_id)
        if cap:
            # We mock the EventBus emission since we are not directly connected in this script
            event_bus.publish({"action": "capability_started", "app": node.arguments.get("app_name"), "dir": node.arguments.get("directory"), "file": node.arguments.get("file_path")})
            
            invocation = ToolInvocation(
                id=str(uuid.uuid4()),
                tool_name=node.tool_name, 
                arguments=node.arguments,
                confidence=1.0,
                source="test_execution"
            )
            out = cap.execute(invocation)
            outputs.append(out)
            
            success = out.execution_result.success
            event_bus.publish({"action": "capability_completed", "app": node.arguments.get("app_name"), "success": success})
            
            # Fault Tolerance: Execution loop continues despite failure
            if not success:
                print(f"[ExecutionRuntime] Fault tolerance invoked for {node.node_id}. Proceeding with graph.")
            
        completed_count += 1
        
    presentation.render_progress("Complete", completed_count, total)
    
    # 3. Verification & Presentation
    delta = verification.evaluate(plan, outputs)
    presentation.render_final(delta)
    
if __name__ == "__main__":
    run_sprint27_execution()
