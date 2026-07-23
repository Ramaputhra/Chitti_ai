import asyncio
import os
import json
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import PlanningDecision, HybridPlanningPolicy
from desktop.brain.runtimes.planner_contracts import IPlannerStrategy
from desktop.platform.strategies.hybrid_planner import HybridPlannerStrategy
from desktop.app.replay_logger import ReplayLogger
from desktop.models.telemetry import PromptReplayRecord, ReplayMode
import datetime

class MockDeterministicPlanner(IPlannerStrategy):
    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        return PlanningDecision(workflow_name="DeterministicWorkflow", confidence=1.0, parameters={}, requires_approval=False)

class MockLLMPlanner(IPlannerStrategy):
    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        return PlanningDecision(workflow_name="LLMWorkflow", confidence=0.85, parameters={}, requires_approval=False)

def test_routing():
    deterministic = MockDeterministicPlanner()
    llm = MockLLMPlanner()
    
    # Test 1: Deterministic
    policy = HybridPlanningPolicy(provider_health="READY", is_offline=False, latency_budget_ms=1000, cost_budget_exceeded=False, session_mode="THOROUGH")
    hybrid = HybridPlannerStrategy(deterministic, llm, policy)
    
    interaction = InteractionEnvelope(id="1", payload="Set timer 10m")
    decision = asyncio.run(hybrid.plan(interaction, MemorySnapshot(episodes=[])))
    assert decision.workflow_name == "DeterministicWorkflow", "Should route to deterministic"
    
    # Test 2: LLM Route
    interaction = InteractionEnvelope(id="2", payload="Explain quantum computing")
    decision = asyncio.run(hybrid.plan(interaction, MemorySnapshot(episodes=[])))
    assert decision.workflow_name == "LLMWorkflow", "Should route to LLM directly"
    
    # Test 3: Offline Fallback
    policy_offline = HybridPlanningPolicy(provider_health="READY", is_offline=True, latency_budget_ms=1000, cost_budget_exceeded=False, session_mode="THOROUGH")
    hybrid_offline = HybridPlannerStrategy(deterministic, llm, policy_offline)
    interaction = InteractionEnvelope(id="3", payload="Explain quantum computing")
    decision = asyncio.run(hybrid_offline.plan(interaction, MemorySnapshot(episodes=[])))
    assert decision.workflow_name == "DeterministicWorkflow", "Should fallback to deterministic when offline"
    print("✅ Routing tests passed")

def test_replay_log():
    log_dir = "logs/replay"
    logger = ReplayLogger(log_dir, mode=ReplayMode.FULL)
    
    record = PromptReplayRecord(
        timestamp=datetime.datetime.now().isoformat(),
        prompt_hash="123abc456def",
        provider_name="test-provider",
        model_name="test-model",
        latency_ms=150.0,
        prompt_tokens=100,
        completion_tokens=20,
        confidence=0.95,
        request_payload="Test prompt",
        response_payload='{"intent": "Test"}',
        validation_outcome="PASS",
        planner_outcome="Pending"
    )
    
    logger.log(record)
    
    # Verify file
    expected_file = os.path.join(log_dir, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.jsonl")
    assert os.path.exists(expected_file), "JSONL file should be created"
    
    with open(expected_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_line = json.loads(lines[-1])
        assert last_line["prompt_hash"] == "123abc456def", "Hash must match"
        assert last_line["request_payload"] == "Test prompt", "Payload must be saved in FULL mode"
        
    print("✅ Replay Logger tests passed")

if __name__ == "__main__":
    print("--- Running Hybrid Planner & Replay Tests (Sprint 86) ---\n")
    test_routing()
    test_replay_log()
    print("\n✅ All Sprint 86 tests passed.")
