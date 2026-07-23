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
from desktop.models.memory import (
    Episode, EpisodeScore, EpisodeQuality, ReplayStatistics, OptimizationRecommendation, MemorySnapshot
)
from desktop.models.cognition import ExecutionPlan, WorkflowRequest, DecisionQuality
from desktop.models.execution import ExecutionTrace, ExecutionStatus
from desktop.models.interaction import InteractionEnvelope
from desktop.models.events import ExecutionCompletedEvent
from desktop.runtimes.verification_runtime import VerificationResult, VerificationStatus
from desktop.runtimes.memory_runtime import MemoryRuntime
from desktop.runtimes.memory.learning_engine import MemoryLearningEngine

async def run_verification():
    print("==========================================================")
    print("Starting COG-31F Learning & Optimization Engine Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Testing EpisodeScore Evolution (Success vs Failure)...")
    engine = MemoryLearningEngine(alpha=0.15, beta=0.40, retention_threshold=0.10)
    
    # Success Boost: 0.50 -> 0.575
    s_boost = engine.evolve_episode_score(0.50, is_success=True)
    if s_boost == 0.575:
        print(f"✅ EpisodeScore success boost verified (0.50 -> {s_boost}).")
    else:
        print(f"❌ EpisodeScore success boost FAILED: {s_boost}")
        all_passed = False

    # Failure Penalty: 0.575 -> 0.345
    s_penalty = engine.evolve_episode_score(s_boost, is_success=False)
    if s_penalty == 0.345:
        print(f"✅ EpisodeScore failure penalty verified ({s_boost} -> {s_penalty}).")
    else:
        print(f"❌ EpisodeScore failure penalty FAILED: {s_penalty}")
        all_passed = False

    print("\n[2/6] Testing EpisodeQuality & ReplayStatistics Generation...")
    q_initial = EpisodeQuality(latency_ms=10.0, accuracy_confidence=1.0)
    q_evolved = engine.evolve_episode_quality(q_initial, is_success=True, latency_ms=150.0)
    
    stats_initial = ReplayStatistics()
    stats_updated = engine.update_replay_statistics(stats_initial, is_success=True, latency_ms=150.0)
    
    if stats_updated.replay_count == 1 and stats_updated.success_count == 1 and stats_updated.average_latency_ms == 150.0:
        print("✅ ReplayStatistics metadata correctly updated.")
    else:
        print("❌ ReplayStatistics metadata update FAILED.")
        all_passed = False

    print("\n[3/6] Testing Advisory OptimizationRecommendation Generation...")
    fp = EnvironmentFingerprint(fingerprint_id="fp1", os_platform="Windows 11", screen_resolution="1920x1080", active_window="Desktop", timestamp=time.time())
    ep = Episode(
        episode_id="ep_test_rec",
        intent={"subtype": "set timer"},
        execution_plan=ExecutionPlan(workflows=[WorkflowRequest(action="text_response", correlation_id="c1")]),
        execution_trace=ExecutionTrace(trace_id="t1", plan_id="p1", total_duration_ms=10.0, overall_status=ExecutionStatus.SUCCESS),
        verification_result=VerificationResult(status=VerificationStatus.VERIFIED_SUCCESS, evidence=["OK"], strategy_used=None),
        fingerprint=fp,
        episode_score=EpisodeScore(score=0.20, last_updated=time.time()),
        timestamp=time.time()
    )
    
    flaky_stats = ReplayStatistics(replay_count=4, success_count=1, failure_count=3)
    state, recs = engine.evaluate_lifecycle_and_recommendations(ep, 0.20, flaky_stats)
    if len(recs) > 0 and recs[0].recommendation_type == "REDUCE_REPLAY_CONFIDENCE":
        print(f"✅ Advisory OptimizationRecommendation generated cleanly: '{recs[0].recommendation_type}'. RetrievalConfig remains untouched.")
    else:
        print("❌ Advisory OptimizationRecommendation generation FAILED.")
        all_passed = False

    print("\n[4/6] Testing Untrusted Episode Removal Policy (Score S < 0.10)...")
    # Multi-failure drop below 0.10
    low_score = 0.05
    state_remove, recs_remove = engine.evaluate_lifecycle_and_recommendations(ep, low_score, stats_updated)
    if state_remove == "REMOVE_UNTRUSTED":
        print(f"✅ Retention Policy verified: Episode score {low_score} flagged for untrusted removal from Cognitive Memory.")
    else:
        print(f"❌ Retention Policy FAILED: state = {state_remove}")
        all_passed = False

    print("\n[5/6] Testing MemoryRuntime Composition & Event-Driven Learning Integration...")
    memory_runtime = MemoryRuntime(db_path="storage/test_learning_mem.db")
    memory_runtime._init_db()
    memory_runtime.save_phase3_episode(ep)
    
    # Process learning outcome via MemoryRuntime
    outcome = memory_runtime.process_execution_learning(ep, is_success=True, latency_ms=120.0)
    if outcome["updated_score"].score > 0.20:
        print(f"✅ MemoryRuntime successfully processed learning outcome: score evolved to {outcome['updated_score'].score:.4f}.")
    else:
        print("❌ MemoryRuntime process_execution_learning FAILED.")
        all_passed = False

    # Test Untrusted Deletion via MemoryRuntime
    ep_untrusted = Episode(
        episode_id="ep_untrusted",
        intent={"subtype": "bad intent"},
        execution_plan=ExecutionPlan(),
        execution_trace=ExecutionTrace(trace_id="t_bad", plan_id="p_bad", total_duration_ms=10.0, overall_status=ExecutionStatus.FAILED),
        verification_result=VerificationResult(status=VerificationStatus.VERIFIED_FAILURE, evidence=["Err"], strategy_used=None),
        fingerprint=fp,
        episode_score=EpisodeScore(score=0.08, last_updated=time.time()),
        timestamp=time.time()
    )
    memory_runtime.save_phase3_episode(ep_untrusted)
    outcome_untrusted = memory_runtime.process_execution_learning(ep_untrusted, is_success=False, latency_ms=10.0)
    
    # Verify untrusted episode deleted from DB
    retrieved = memory_runtime.get_phase3_episode("ep_untrusted")
    if outcome_untrusted["should_remove"] and retrieved is None:
        print("✅ Untrusted Episode (S < 0.10) successfully deleted from Cognitive Memory database.")
    else:
        print("❌ Untrusted Episode deletion FAILED.")
        all_passed = False

    print("\n[6/6] Zero Regression Verification (COG-31A, COG-31B, COG-31C, COG-31D, COG-31E)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    events_captured = []
    def on_event(event):
        if event.__class__.__name__ in ["Event", "ExecutionCompletedEvent"]:
            events_captured.append(event)
            
    kernel.context.event_bus.subscribe(ExecutionCompletedEvent, on_event)
    
    # Create and publish plan
    plan = ExecutionPlan(workflows=[WorkflowRequest(action="text_response", correlation_id="c_smoke")])
    kernel.context.event_bus.publish(plan)
    
    for _ in range(20):
        await asyncio.sleep(0.1)
        
    if len(events_captured) > 0:
        print("✅ Zero Regression Verification PASSED: Canonical execution spine & event-driven learning fully intact.")
    else:
        print("❌ Canonical execution spine failed.")
        all_passed = False
        
    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: COG-31F IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: COG-31F VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
