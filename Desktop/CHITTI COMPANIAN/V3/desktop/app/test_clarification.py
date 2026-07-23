import asyncio
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import PlanningDecision, HybridPlanningPolicy, PlanningRoute
from desktop.brain.runtimes.planner_contracts import IPlannerStrategy
from desktop.platform.strategies.hybrid_planner import HybridPlannerStrategy
from desktop.app.intent_manager import PendingIntentStore

class MockDeterministicPlanner(IPlannerStrategy):
    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        return PlanningDecision(workflow_name="FallbackWorkflow", confidence=0.0, parameters={}, requires_approval=False)

class MockLLMPlanner(IPlannerStrategy):
    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        return PlanningDecision(workflow_name="UnknownIntentWorkflow", confidence=0.0, parameters={}, requires_approval=False)

class MockClarificationPlanner(IPlannerStrategy):
    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        return PlanningDecision(
            workflow_name="ClarificationWorkflow", 
            confidence=0.9, 
            parameters={"question": "For how long?", "missing_parameter": "duration"}, 
            requires_approval=False
        )

def test_clarification_flow():
    deterministic = MockDeterministicPlanner()
    llm = MockLLMPlanner()
    clarification = MockClarificationPlanner()
    policy = HybridPlanningPolicy(provider_health="READY", is_offline=False, latency_budget_ms=1000, cost_budget_exceeded=False, session_mode="THOROUGH")
    store = PendingIntentStore()
    
    hybrid = HybridPlannerStrategy(deterministic, llm, clarification, policy, store)
    
    # 1. Trigger Clarification
    interaction = InteractionEnvelope(id="c_123", payload="Set a timer")
    decision = asyncio.run(hybrid.plan(interaction, MemorySnapshot(episodes=[])))
    
    assert decision.workflow_name == "ClarificationWorkflow", "Should fallback and route to clarification"
    assert "workflow_id" in decision.parameters, "Should generate a PendingIntent workflow_id"
    
    workflow_id = decision.parameters["workflow_id"]
    pending = store.get(workflow_id)
    assert pending is not None, "PendingIntent should be stored"
    assert "duration" in pending.missing_parameters, "Missing parameter captured"
    
    # 2. Resume (simulating providing the missing parameter)
    interaction2 = InteractionEnvelope(id="c_124", payload="10 minutes")
    
    # Normally a generic Intent resolution node or the workflow itself would intercept this
    # For testing, we ensure that if we fetch it by correlation ID or if the interaction was routed to it, the intent is there.
    assert store.get_by_correlation("c_123") == pending
    
    # Simulate resolving
    store.remove(workflow_id)
    assert store.get(workflow_id) is None
    
    print("✅ Clarification routing and PendingIntent tests passed")

if __name__ == "__main__":
    print("--- Running Clarification Tests (Sprint 88) ---\n")
    test_clarification_flow()
    print("\n✅ All Sprint 88 tests passed.")
