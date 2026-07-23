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
from desktop.packages.desktop_pack.capabilities.resume_work import ResumeWorkCapability
from desktop.models.capability import CanonicalCapabilityOutput

class VerboseLogger(ILoggingService):
    def info(self, msg: str) -> None: print(f"[INFO] {msg}")
    def error(self, msg: str) -> None: print(f"[ERROR] {msg}")
    def warning(self, msg: str) -> None: print(f"[WARN] {msg}")
    def debug(self, msg: str) -> None: print(f"[DEBUG] {msg}")
    def exception(self, msg: str, exc: Exception) -> None: print(f"[EXCEPTION] {msg}: {exc}")

class MockPlannerRuntime:
    def route_intent(self, intent_name: str, args: dict):
        print(f"[PlannerRuntime] Orchestrating Workflow for {intent_name} with args {args}")
        return {
            "capability_id": "ResumeWorkCapability",
            "tool_name": intent_name,
            "params": args
        }
        
class MockConversationRuntime:
    def __init__(self):
        self.active_plan = None
        
    def handle_canonical_output(self, output: CanonicalCapabilityOutput):
        artifact = output.conversation_artifact
        if hasattr(artifact, "restore_plan") and artifact.restore_plan:
            self.active_plan = artifact.restore_plan
            print(f"[ConversationRuntime] Retaining immutable WorkspaceRestorePlan for {self.active_plan.workspace_name}")
            
    def handle_followup(self, user_text: str, is_information: bool = False):
        print(f"\n==========================================================")
        print(f"[User Interaction] Follow-up command: '{user_text}'")
        if self.active_plan:
            print(f"[ConversationRuntime] Reusing existing WorkspaceRestorePlan for '{self.active_plan.workspace_name}'")
            if is_information:
                summary = self.active_plan.to_summary()
                print(f"[ConversationRuntime] Derived lightweight WorkspaceRestoreSummary.")
                print(f"[ConversationRuntime] Generating explanation using WorkspaceRestoreSummary.")
                print(f"[PresentationRuntime] Rendering explanation artifact.")
                print(f"[ExecutionRuntime] BYPASSED. Spine not traversed.")
            else:
                print(f"[PlannerRuntime] Filtering plan based on action intent -> extracting requested components.")
                print(f"[ExecutionRuntime] Executing only filtered components.")
        else:
            print("[ConversationRuntime] No active plan found.")

class MockVerificationRuntime:
    def verify(self, output: CanonicalCapabilityOutput):
        vr = output.verification_result
        if vr and vr.verification_strategy == "WorkspaceStateComparison":
            print(f"[VerificationRuntime] Verifying Expected Workspace vs Observed Workspace")
            print(f"[VerificationRuntime] Targets: {vr.evidence_ids}")
            print(f"[VerificationRuntime] Status: VERIFIED")

def run_sprint26_validation():
    logger = VerboseLogger()
    event_bus = InMemoryEventBus()
    event_bus.initialize()
    
    registry = RuntimeCapabilityRegistry(logger)
    registry.initialize()
    
    print("\n==========================================================")
    print("RuntimeCapabilityRegistry Registration")
    print("==========================================================")
    cap = ResumeWorkCapability()
    registry.register_capability(cap)
    print(f"Registered Capability: {cap.name}")
    
    execution_runtime = ExecutionRuntime(registry, event_bus)
    planner = MockPlannerRuntime()
    conversation = MockConversationRuntime()
    verification = MockVerificationRuntime()

    print("\n==========================================================")
    print("Scenario: General Workspace Restore")
    print("==========================================================")
    print("[User Interaction] Command: 'Resume my work'")
    print("[AIRuntime] Resolved Intent -> resume_activity")
    
    workflow_def = planner.route_intent("resume_activity", {"project_name": "AI Development"})
    
    # We will invoke the capability manually here just like the stub does
    cap_instance = registry.get_capability(workflow_def["capability_id"])
    print(f"[ExecutionRuntime] Traversing spine to invoke ToolInvocation")
    
    from desktop.platform.shared.models.ai import ToolInvocation
    invocation = ToolInvocation(
        tool_name=workflow_def["tool_name"],
        arguments=workflow_def["params"]
    )
    
    # Execute Capability
    canonical_output = cap_instance.execute(invocation)
    
    print("[ExecutionRuntime] Canonical Output generated successfully.")
    
    # Simulate semantic consumption
    conversation.handle_canonical_output(canonical_output)
    verification.verify(canonical_output)
    
    # Presentation
    print(f"[PresentationRuntime] Rendering {canonical_output.presentation_descriptor.recipe_id} with data keys: {list(canonical_output.presentation_descriptor.layout_data.keys())}")
    
    # Follow-up scenarios
    conversation.handle_followup("Restore browser only", is_information=False)
    conversation.handle_followup("Restore only VS Code", is_information=False)
    conversation.handle_followup("Restore everything except terminal", is_information=False)
    conversation.handle_followup("Explain this workspace", is_information=True)
    conversation.handle_followup("Why is confidence low?", is_information=True)

if __name__ == "__main__":
    run_sprint26_validation()
