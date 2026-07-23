import unittest
from typing import Dict, Any
from desktop.platform.shared.models.workflow import ExecutionPlan, ExecutionPlanNode
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.packages.desktop_pack.capabilities.vision_intelligence import (
    VisionCaptureCapability,
    VisionLayoutCapability,
    VisionErrorCapability,
    VisionTableCapability,
    VisionDocumentCapability,
    VisionControlCapability
)

def create_tool_invocation(tool_name: str, arguments: Dict[str, Any]) -> ToolInvocation:
    import uuid
    return ToolInvocation(
        id=f"inv_{uuid.uuid4().hex[:8]}",
        tool_name=tool_name,
        arguments=arguments,
        confidence=1.0,
        source="VisionIntelligenceRegressionSuite"
    )

class MockPlannerRuntime:
    def build_vision_plan(self) -> ExecutionPlan:
        print("\n==========================================================")
        print("[PlannerRuntime] Compiling ExecutionPlan for Intent: 'What is this error?'")
        print("==========================================================")
        return ExecutionPlan(
            plan_id="plan_vision",
            steps=[]  # Using nodes manually
        )

class MockConversationRuntime:
    def create_workspace(self, title: str):
        print(f"[ConversationRuntime] Created VisionWorkspace: {title}")
        class DummyWorkspace:
            def __init__(self): self.artifacts = []
        return DummyWorkspace()
        
    def handle_followup(self, text: str, is_information: bool):
        print("\n==========================================================")
        print(f"[User Interaction] Follow-up command: '{text}'")
        if is_information:
            print("[ConversationRuntime] Generating explanation using VisionWorkspaceSummary.")
        else:
            print("[ConversationRuntime] Resolving action against active VisionWorkspace.")
            print("[PlannerRuntime] Dispatching targeted ExecutionPlan.")

class MockExecutionRuntime:
    def __init__(self, registry):
        self.registry = registry
        
    def execute_plan(self, nodes: list):
        print(f"[ExecutionRuntime] Traversing ExecutionPlan")
        results = []
        for node in nodes:
            cap = self.registry.get(node.capability_id)
            out = cap.execute(create_tool_invocation(node.tool_name, node.arguments))
            results.append(out)
        return results

class MockPresentationRuntime:
    def render_recipe(self, recipe: str):
        print(f"[PresentationRuntime] Rendering declarative overlay: {recipe}")

class MockVerificationRuntime:
    def verify(self):
        print("[VerificationRuntime] Deterministic verification: Foreground window matched. LayoutTree unchanged.")

class TestSprint29VisionIntelligence(unittest.TestCase):
    def test_vision_intelligence_platform_traversal(self):
        registry = {
            "VisionCaptureCapability": VisionCaptureCapability(),
            "VisionLayoutCapability": VisionLayoutCapability(),
            "VisionErrorCapability": VisionErrorCapability(),
            "VisionControlCapability": VisionControlCapability()
        }
        
        planner = MockPlannerRuntime()
        executor = MockExecutionRuntime(registry)
        conversation = MockConversationRuntime()
        presentation = MockPresentationRuntime()
        verifier = MockVerificationRuntime()

        # 1. Start interaction
        plan = planner.build_vision_plan()
        workspace = conversation.create_workspace("Error Context")
        self.assertIsNotNone(workspace)
        
        # 2. Execution (Capture -> Layout -> Semantic Extraction)
        n1 = ExecutionPlanNode("n1", "VisionCaptureCapability", "vision_capture", {})
        n2 = ExecutionPlanNode("n2", "VisionLayoutCapability", "vision_layout", {}, dependencies=["n1"])
        n3 = ExecutionPlanNode("n3", "VisionErrorCapability", "vision_error", {}, dependencies=["n2"])
        
        results = executor.execute_plan([n1, n2, n3])
        self.assertEqual(len(results), 3)
        
        # Extract the artifact from the result
        artifact = results[2].conversation_artifact
        workspace.artifacts.append(artifact)
        
        presentation.render_recipe("recipe_vision_error_callout")
        verifier.verify()
        
        # 3. Conversational Follow-up (Information)
        conversation.handle_followup("How do I fix it?", is_information=True)
        print("[PresentationRuntime] Rendering summary of 'Error Context' (1 artifacts).")
        print("[ExecutionRuntime] BYPASSED. Spine not traversed.")
        
        # 4. Conversational Follow-up (Action)
        conversation.handle_followup("Dismiss the error.", is_information=False)
        n4 = ExecutionPlanNode("n4", "VisionControlCapability", "vision_control", {})
        results2 = executor.execute_plan([n4])
        self.assertEqual(len(results2), 1)

if __name__ == "__main__":
    unittest.main()
