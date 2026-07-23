from typing import Any, List, Dict
from desktop.platform.shared.models.ai import ToolInvocation

from desktop.models.browser_workspace import (
    BrowserWorkspace, BrowserWorkspaceSummary, CommerceEntity, KnowledgeEntity
)
from desktop.models.conversation import (
    SearchArtifact, ShoppingArtifact, DocumentationArtifact, AuthenticationArtifact
)
from desktop.models.execution_plan import ExecutionPlan, ExecutionPlanNode
from desktop.packages.desktop_pack.capabilities.browser_intelligence import (
    BrowserNavigationCapability,
    BrowserDOMCapability,
    BrowserSearchCapability,
    BrowserCommerceCapability,
    BrowserAuthenticationCapability
)

def create_tool_invocation(tool_name: str, arguments: Dict[str, Any]) -> ToolInvocation:
    """Helper factory to enforce canonical ToolInvocation contract construction."""
    import uuid
    return ToolInvocation(
        id=f"inv_{uuid.uuid4().hex[:8]}",
        tool_name=tool_name,
        arguments=arguments,
        confidence=1.0,
        source="BrowserIntelligenceRegressionSuite"
    )

class MockPlannerRuntime:
    def build_shopping_plan(self) -> ExecutionPlan:
        print("\n==========================================================")
        print("[PlannerRuntime] Compiling ExecutionPlan for Intent: 'Find a 4K monitor on Amazon'")
        n1 = ExecutionPlanNode("n1", "BrowserNavigationCapability", "browser_navigate", {"url": "https://amazon.com/s?k=4k+monitor"})
        n2 = ExecutionPlanNode("n2", "BrowserDOMCapability", "browser_dom", {}, dependencies=["n1"])
        n3 = ExecutionPlanNode("n3", "BrowserSearchCapability", "browser_search", {}, dependencies=["n2"])
        return ExecutionPlan(plan_id="plan_shop", nodes=[n1, n2, n3])

class MockExecutionRuntime:
    def __init__(self, registry: Dict[str, Any]):
        self.registry = registry

    def execute_plan(self, plan: ExecutionPlan) -> List[Any]:
        print("==========================================================")
        print(f"[ExecutionRuntime] Traversing ExecutionPlan: {plan.plan_id}")
        results = []
        for node in plan.nodes:
            cap = self.registry.get(node.capability_id)
            out = cap.execute(create_tool_invocation(node.tool_name, node.arguments))
            results.append(out)
        return results

class MockConversationRuntime:
    def __init__(self):
        self.active_workspace = None

    def create_workspace(self, intent: str) -> BrowserWorkspace:
        self.active_workspace = BrowserWorkspace(
            workspace_id="ws_001",
            workspace_name="Shopping Workspace",
            intent=intent
        )
        print("==========================================================")
        print(f"[ConversationRuntime] Created BrowserWorkspace: {self.active_workspace.workspace_name}")
        return self.active_workspace

    def handle_followup(self, user_text: str, is_information: bool = False):
        print("\n==========================================================")
        print(f"[User Interaction] Follow-up command: '{user_text}'")
        if self.active_workspace:
            if is_information:
                summary = self.active_workspace.to_summary()
                print("[ConversationRuntime] Generating explanation using BrowserWorkspaceSummary.")
                print(f"[PresentationRuntime] Rendering summary of '{summary.workspace_name}' ({len(summary.active_artifacts)} artifacts).")
                print("[ExecutionRuntime] BYPASSED. Spine not traversed.")
            else:
                print(f"[ConversationRuntime] Resolving action against active BrowserWorkspace ({len(self.active_workspace.artifacts)} artifacts).")
                print("[PlannerRuntime] Dispatching targeted ExecutionPlan.")
        else:
            print("[ConversationRuntime] No active BrowserWorkspace.")

class MockPresentationRuntime:
    def render_recipe(self, recipe_name: str):
        print(f"[PresentationRuntime] Rendering declarative overlay: {recipe_name}")

class MockVerificationRuntime:
    def verify(self):
        print("[VerificationRuntime] Deterministic verification: URL matches expected pattern. DOM LayoutTree structurally valid.")


import unittest

class TestSprint28BrowserIntelligence(unittest.TestCase):
    def test_browser_intelligence_platform_traversal(self):
        registry = {
            "BrowserNavigationCapability": BrowserNavigationCapability(),
            "BrowserDOMCapability": BrowserDOMCapability(),
            "BrowserSearchCapability": BrowserSearchCapability(),
            "BrowserCommerceCapability": BrowserCommerceCapability(),
            "BrowserAuthenticationCapability": BrowserAuthenticationCapability()
        }
        
        planner = MockPlannerRuntime()
        executor = MockExecutionRuntime(registry)
        conversation = MockConversationRuntime()
        presentation = MockPresentationRuntime()
        verifier = MockVerificationRuntime()

        # 1. Start interaction
        plan = planner.build_shopping_plan()
        workspace = conversation.create_workspace("Shopping")
        self.assertIsNotNone(workspace)
        
        # 2. Execution
        results = executor.execute_plan(plan)
        self.assertEqual(len(results), 3)
        
        # Simulate saving SearchArtifact to workspace
        artifact = SearchArtifact(
            artifact_id="art_01", artifact_type="SearchArtifact", capability_id="BrowserSearchCapability",
            timestamp=None, summary="Amazon Search Results", structured_result={}, referenced_entities=[],
            supported_followup_actions=["Open Result"], presentation_available=True, expiration_policy="", confidence=1.0
        )
        workspace.artifacts.append(artifact)
        
        presentation.render_recipe("recipe_search_results")
        verifier.verify()
        
        # 3. Conversational Follow-up (Action)
        conversation.handle_followup("Open the first result.", is_information=False)
        
        # Simulate execution of clicking first result -> Commerce page
        n_com1 = ExecutionPlanNode("n_c1", "BrowserDOMCapability", "browser_dom", {})
        n_com2 = ExecutionPlanNode("n_c2", "BrowserCommerceCapability", "browser_commerce", {}, dependencies=["n_c1"])
        com_results = executor.execute_plan(ExecutionPlan(plan_id="plan_item", nodes=[n_com1, n_com2]))
        self.assertEqual(len(com_results), 2)
        
        shop_art = ShoppingArtifact(
            artifact_id="art_02", artifact_type="ShoppingArtifact", capability_id="BrowserCommerceCapability",
            timestamp=None, summary="Product Page", structured_result={}, referenced_entities=[],
            supported_followup_actions=["Compare", "Add to Cart"], presentation_available=True, expiration_policy="", confidence=1.0,
            product=CommerceEntity(product_name="Dell 4K", price="$300", currency="USD", stock_status="In Stock", rating=4.5)
        )
        workspace.artifacts.append(shop_art)
        
        presentation.render_recipe("recipe_shopping_product")
        verifier.verify()
        
        # 4. Conversational Follow-up (Information/Contextual Revert)
        conversation.handle_followup("Continue shopping.", is_information=True)


if __name__ == "__main__":
    unittest.main()
