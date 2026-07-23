import sys
import os
import time
import asyncio
from datetime import datetime

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.capability.registry import CapabilityRegistry

from desktop.models.environment import EnvironmentFingerprint
from desktop.models.memory import Episode, EpisodeScore, EpisodeQuality, MemorySnapshot
from desktop.models.cognition import ExecutionPlan, WorkflowRequest, ExecutionPolicy, ApprovalRequirement, DecisionQuality, PlanningDecision
from desktop.models.execution import ExecutionTrace, ExecutionStep, ExecutionStatus
from desktop.models.interaction import InteractionEnvelope
from desktop.models.events import ExecutionCompletedEvent
from desktop.runtimes.verification_runtime import VerificationResult, VerificationStatus
from desktop.platform.strategies.memory_replay import MemoryReplayStrategy
from desktop.platform.strategies.hybrid_planner import HybridPlannerStrategy
from desktop.app.planner_contracts import IPlannerStrategy

async def run_verification():
    print("==========================================================")
    print("Starting COG-31E Episode Replay Engine Verification")
    print("==========================================================\n")
    
    all_passed = True

    # Setup Cap Registry & Strategy
    cap_registry = CapabilityRegistry()
    replay_strategy = MemoryReplayStrategy(capability_registry=cap_registry, confidence_threshold=0.70)
    
    # 1. Register Capability in Registry for Availability Check
    from desktop.runtimes.capability.provider import CapabilityProvider
    provider = CapabilityProvider(cap_registry)
    provider.register_all()

    # Create Baseline Replayable Episode
    fp = EnvironmentFingerprint(
        fingerprint_id="fp_orig",
        os_platform="Windows 11",
        screen_resolution="1920x1080",
        active_window="Desktop",
        timestamp=time.time()
    )
    plan = ExecutionPlan(
        approval=ApprovalRequirement(required=False, reason="Verification"),
        workflows=[
            WorkflowRequest(action="text_response", parameters={"text": "Historical Response"}, policy=ExecutionPolicy(timeout=10.0), correlation_id="corr_orig")
        ]
    )
    trace = ExecutionTrace(trace_id="tr_orig", plan_id="plan_orig", total_duration_ms=50.0, overall_status=ExecutionStatus.SUCCESS)
    v_res = VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=["Fallback"], strategy_used=None)
    score = EpisodeScore(score=0.95, last_updated=time.time())
    quality = EpisodeQuality(latency_ms=50.0, accuracy_confidence=0.99)

    valid_episode = Episode(
        episode_id="ep_replay_31e",
        intent={"subtype": "text_response", "query": "say hello"},
        execution_plan=plan,
        execution_trace=trace,
        verification_result=v_res,
        fingerprint=fp,
        timestamp=time.time(),
        episode_score=score,
        episode_quality=quality
    )

    memory_snapshot = MemorySnapshot(
        session_id="s1",
        episodes=[valid_episode]
    )
    setattr(memory_snapshot, "environment_fingerprint", fp)

    print("[1/5] Testing Candidate Retrieval & Eligibility Evaluation...")
    interaction = InteractionEnvelope(
        id="int_1",
        session_id="s1",
        timestamp=datetime.now(),
        origin="CLI",
        transport="CLI",
        payload="say hello",
        metadata={"text": "Fresh Dynamic Payload"}
    )

    decision = await replay_strategy.plan(interaction, memory_snapshot)
    if decision and decision.confidence != DecisionQuality.REJECTED:
        print("✅ Replay Strategy recommended replay with high confidence.")
    else:
        print("❌ Replay Strategy failed to recommend replay.")
        all_passed = False

    print("\n[2/5] Testing Refinements: Embedded ExecutionPlan & Explanation Payload...")
    rebound_plan = getattr(decision, "plan", None)
    explanation = getattr(decision, "explanation", {})
    
    if isinstance(rebound_plan, ExecutionPlan) and rebound_plan.workflows:
        print("✅ Refinement #1: Rebound ExecutionPlan is embedded inside PlanningDecision.")
    else:
        print("❌ Refinement #1: PlanningDecision missing embedded ExecutionPlan.")
        all_passed = False

    required_keys = ["intent_similarity", "fingerprint_compatibility", "episode_score", "episode_quality", "capability_availability"]
    if all(k in explanation for k in required_keys):
        print(f"✅ Refinement #2: Explanation payload present with all 5 metrics ({explanation}).")
    else:
        print(f"❌ Refinement #2: Explanation payload missing required keys: {explanation}")
        all_passed = False

    print("\n[3/5] Testing Fingerprint Comparison & Parameter Rebinding...")
    rebound_text = rebound_plan.workflows[0].parameters.get("text")
    if rebound_text == "Fresh Dynamic Payload":
        print(f"✅ Dynamic Parameter Rebinding PASSED (New payload '{rebound_text}' injected).")
    else:
        print(f"❌ Parameter Rebinding FAILED (Got '{rebound_text}').")
        all_passed = False

    # Test Mismatched OS Rejection
    mismatched_fp = EnvironmentFingerprint(fingerprint_id="fp_linux", os_platform="Linux", screen_resolution="1920x1080", active_window="Terminal", timestamp=time.time())
    setattr(memory_snapshot, "environment_fingerprint", mismatched_fp)
    mismatched_decision = await replay_strategy.plan(interaction, memory_snapshot)
    if mismatched_decision.confidence == DecisionQuality.REJECTED:
        print("✅ Hard Fingerprint Mismatch (OS Linux vs Windows) correctly REJECTED replay.")
    else:
        print("❌ Fingerprint Mismatch Rejection FAILED.")
        all_passed = False

    print("\n[4/5] Testing LLM Fallback Routing in HybridPlannerStrategy...")
    # Restore valid fingerprint
    setattr(memory_snapshot, "environment_fingerprint", fp)
    
    # Mock deterministic fallback planner
    class DummyPlanner(IPlannerStrategy):
        def parse_intent(self, i, c): pass
        def formulate_decision(self, i, c): pass
        def create_plan(self, d, i, s): pass
        async def plan(self, i, m):
            return PlanningDecision(plan=ExecutionPlan(workflows=[WorkflowRequest(action="fallback_action", correlation_id="c_fb")]), confidence=DecisionQuality.CERTAIN)

    hybrid = HybridPlannerStrategy(
        deterministic_planner=DummyPlanner(),
        llm_planner=DummyPlanner(),
        clarification_planner=DummyPlanner(),
        policy=None,
        intent_store=None,
        replay_strategy=replay_strategy
    )

    # Test Replay Route Accept
    hybrid_decision = await hybrid.plan(interaction, memory_snapshot)
    if hybrid_decision and getattr(getattr(hybrid_decision, "plan", None), "workflows", [{}])[0].action == "text_response":
        print("✅ HybridPlannerStrategy accepted Replay decision over fallback.")
    else:
        print("❌ HybridPlannerStrategy failed to route to Replay.")
        all_passed = False

    # Test Fallback Route on Empty Memory
    empty_memory = MemorySnapshot(session_id="s1", episodes=[])
    fallback_decision = await hybrid.plan(interaction, empty_memory)
    if fallback_decision and getattr(getattr(fallback_decision, "plan", None), "workflows", [{}])[0].action == "fallback_action":
        print("✅ HybridPlannerStrategy cleanly fell back to fallback planner on empty memory.")
    else:
        print("❌ HybridPlannerStrategy fallback routing FAILED.")
        all_passed = False

    print("\n[5/5] Executing Replayed ExecutionPlan through Production Runtime Pipeline...")
    config = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config)
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    events_captured = []
    def on_event(event):
        if event.__class__.__name__ in ["Event", "ExecutionCompletedEvent"]:
            events_captured.append(event)
            
    kernel.context.event_bus.subscribe(ExecutionCompletedEvent, on_event)
    
    # Publish rebound plan to EventBus
    kernel.context.event_bus.publish(rebound_plan)
    for _ in range(20):
        await asyncio.sleep(0.1)
        
    if len(events_captured) > 0:
        print("✅ Replayed plan successfully completed canonical execution spine & emitted ExecutionCompletedEvent.")
    else:
        print("❌ Replayed plan execution failed to emit ExecutionCompletedEvent.")
        all_passed = False
        
    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: COG-31E IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: COG-31E VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
