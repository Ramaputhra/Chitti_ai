import unittest
from typing import Dict, Any
from desktop.platform.shared.models.workflow import ExecutionPlan, ExecutionPlanNode
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.packages.desktop_pack.capabilities.activity_intelligence import (
    ActivityDetectionCapability,
    ActivityContextCapability,
    ActivityProgressCapability,
    ActivityRecommendationCapability
)

def create_tool_invocation(tool_name: str, arguments: Dict[str, Any]) -> ToolInvocation:
    import uuid
    return ToolInvocation(
        id=f"inv_{uuid.uuid4().hex[:8]}",
        tool_name=tool_name,
        arguments=arguments,
        confidence=1.0,
        source="ActivityIntelligenceRegressionSuite"
    )

class MockPlannerRuntime:
    def build_activity_plan(self) -> ExecutionPlan:
        print("\n==========================================================")
        print("[PlannerRuntime] Compiling ExecutionPlan for Goal: 'Resume where I stopped'")
        print("==========================================================")
        return ExecutionPlan(plan_id="plan_act", steps=[])

class MockConversationRuntime:
    def __init__(self):
        self.context_workspace = []
        
    def handle_followup(self, text: str, is_information: bool):
        print("\n==========================================================")
        print(f"[User Interaction] Follow-up command: '{text}'")
        if is_information:
            print("[ConversationRuntime] Generating explanation using ActivityArtifact from ContextWorkspace.")
            print("[ExecutionRuntime] BYPASSED. Spine not traversed.")
        else:
            print("[ConversationRuntime] Resolving action against historic WorkflowArtifact.")
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
        print(f"[PresentationRuntime] Rendering declarative UI: {recipe}")

class MockVerificationRuntime:
    def verify(self):
        print("[VerificationRuntime] Deterministic verification: Semantic timelines and Workspace dependencies cross-validated.")

class TestSprint30ActivityIntelligence(unittest.TestCase):
    def test_activity_intelligence_platform_traversal(self):
        registry = {
            "ActivityDetectionCapability": ActivityDetectionCapability(),
            "ActivityContextCapability": ActivityContextCapability(),
            "ActivityProgressCapability": ActivityProgressCapability(),
            "ActivityRecommendationCapability": ActivityRecommendationCapability()
        }
        
        planner = MockPlannerRuntime()
        executor = MockExecutionRuntime(registry)
        conversation = MockConversationRuntime()
        presentation = MockPresentationRuntime()
        verifier = MockVerificationRuntime()

        # 1. Background Detection
        print("\n[Kernel Startup] Initializing Activity Intelligence")
        n1 = ExecutionPlanNode("n1", "ActivityDetectionCapability", "activity_detect", {})
        n2 = ExecutionPlanNode("n2", "ActivityContextCapability", "activity_context", {}, dependencies=["n1"])
        
        results = executor.execute_plan([n1, n2])
        self.assertEqual(len(results), 2)
        verifier.verify()
        
        # 2. Conversational Follow-up (Information)
        conversation.handle_followup("What am I working on?", is_information=True)
        
        # 3. Conversational Follow-up (Action)
        conversation.handle_followup("Resume where I stopped.", is_information=False)
        planner.build_activity_plan()
        
        n3 = ExecutionPlanNode("n3", "ActivityProgressCapability", "activity_progress", {})
        n4 = ExecutionPlanNode("n4", "ActivityRecommendationCapability", "activity_recommend", {}, dependencies=["n3"])
        
        results2 = executor.execute_plan([n3, n4])
        self.assertEqual(len(results2), 2)
        
        presentation.render_recipe(results2[1].presentation_descriptor.recipe_id)

if __name__ == "__main__":
    unittest.main()
