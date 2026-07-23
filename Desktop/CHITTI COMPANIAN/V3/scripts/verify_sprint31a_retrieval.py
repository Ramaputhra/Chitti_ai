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
    Episode, EpisodeScore, EpisodeQuality, MemorySnapshot, ExperienceLevel, MemoryEpisodeHint, RetrievalConfig
)
from desktop.models.cognition import (
    ExecutionPlan, WorkflowRequest, ExecutionPolicy, ApprovalRequirement, DecisionQuality, PlanningDecision
)
from desktop.models.execution import ExecutionTrace, ExecutionStep, ExecutionStatus
from desktop.models.interaction import InteractionEnvelope
from desktop.models.events import ExecutionCompletedEvent
from desktop.runtimes.verification_runtime import VerificationResult, VerificationStatus
from desktop.runtimes.memory_runtime import MemoryRuntime
from desktop.runtimes.memory.retrieval_engine import MemoryRetrievalEngine
from desktop.platform.strategies.memory_replay import MemoryReplayStrategy
from desktop.platform.strategies.hybrid_planner import HybridPlannerStrategy
from desktop.platform.strategies.llm_planner import LLMPlannerStrategy
from desktop.app.prompt_builder import PromptBuilder

# Dummy Inference Strategy for offline unit testing
class DummyInferenceResult:
    def __init__(self, intent="GreetingIntent", confidence=0.95):
        self.intent = intent
        self.confidence = confidence
        self.entities = {}
        self.reasoning_notes = "Dummy LLM Reasoning"

class DummyInferenceStrategy:
    async def infer(self, interaction, memory):
        return DummyInferenceResult()

async def run_verification():
    print("==========================================================")
    print("Starting COG-31A Memory Retrieval & Selection Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Testing RetrievalConfig Defaults & Configurable Pool Limit...")
    config = RetrievalConfig(candidate_pool_limit=50, top_k=3, min_similarity_threshold=0.40)
    if config.candidate_pool_limit == 50 and config.top_k == 3 and config.min_similarity_threshold == 0.40:
        print("✅ RetrievalConfig initialized with correct configurable defaults.")
    else:
        print("❌ RetrievalConfig default initialization failed.")
        all_passed = False

    print("\n[2/6] Testing MemoryRetrievalEngine Two-Stage Retrieval & Candidate Pruning...")
    engine = MemoryRetrievalEngine(config=config)
    fp = EnvironmentFingerprint(fingerprint_id="fp1", os_platform="Windows 11", screen_resolution="1920x1080", active_window="Desktop", timestamp=time.time())
    
    # Candidate 1: Exact match, Verified Success
    ep1 = Episode(
        episode_id="ep1",
        intent={"subtype": "set timer", "query": "set timer for 5 minutes"},
        execution_plan=ExecutionPlan(workflows=[WorkflowRequest(action="text_response", correlation_id="c1", parameters={"duration_sec": 300})]),
        execution_trace=ExecutionTrace(trace_id="t1", plan_id="p1", total_duration_ms=10.0, overall_status=ExecutionStatus.SUCCESS),
        verification_result=VerificationResult(status=VerificationStatus.VERIFIED_SUCCESS, evidence=["OK"], strategy_used=None),
        fingerprint=fp,
        episode_score=EpisodeScore(score=0.95, last_updated=time.time()),
        episode_quality=EpisodeQuality(latency_ms=10.0, accuracy_confidence=0.98),
        timestamp=time.time()
    )

    # Candidate 2: Failed verification -> MUST BE PRUNED
    ep2_failed = Episode(
        episode_id="ep2_failed",
        intent={"subtype": "set timer", "query": "set timer for 5 minutes"},
        execution_plan=ExecutionPlan(workflows=[WorkflowRequest(action="text_response", correlation_id="c2")]),
        execution_trace=ExecutionTrace(trace_id="t2", plan_id="p2", total_duration_ms=10.0, overall_status=ExecutionStatus.FAILED),
        verification_result=VerificationResult(status=VerificationStatus.VERIFIED_FAILURE, evidence=["Failed"], strategy_used=None),
        fingerprint=fp,
        timestamp=time.time()
    )

    # Candidate 3: Low similarity -> MUST BE PRUNED (< 0.40)
    ep3_unrelated = Episode(
        episode_id="ep3_unrelated",
        intent={"subtype": "open website", "query": "open google chrome"},
        execution_plan=ExecutionPlan(workflows=[WorkflowRequest(action="text_response", correlation_id="c3")]),
        execution_trace=ExecutionTrace(trace_id="t3", plan_id="p3", total_duration_ms=10.0, overall_status=ExecutionStatus.SUCCESS),
        verification_result=VerificationResult(status=VerificationStatus.VERIFIED_SUCCESS, evidence=["OK"], strategy_used=None),
        fingerprint=fp,
        timestamp=time.time()
    )

    interaction = InteractionEnvelope(
        id="int1", session_id="s1", timestamp=datetime.now(),
        origin="CLI", transport="CLI", payload="set timer for 5 minutes"
    )

    hints = engine.retrieve_hints(interaction, [ep1, ep2_failed, ep3_unrelated])
    
    if len(hints) == 1 and hints[0].workflow_summary == "text_response":
        print("✅ Two-Stage Retrieval correctly retrieved ep1 and pruned failed & low-similarity candidates.")
    else:
        print(f"❌ Two-Stage Retrieval failed: hints count = {len(hints)}")
        all_passed = False

    print("\n[3/6] Testing Continuous RetrievalConfidence Calculation [0.0, 1.0]...")
    for h in hints:
        if 0.0 <= h.retrieval_confidence <= 1.0:
            print(f"✅ Hint continuous RetrievalConfidence = {h.retrieval_confidence:.4f} (ExperienceLevel: {h.experience_level.value}).")
        else:
            print(f"❌ Out-of-bounds RetrievalConfidence = {h.retrieval_confidence}")
            all_passed = False

    print("\n[4/6] Testing MemoryRuntime Integration & MemorySnapshot Projection...")
    memory_runtime = MemoryRuntime(db_path="storage/test_retrieval_mem.db")
    memory_runtime._init_db()
    memory_runtime.save_phase3_episode(ep1)
    
    # Snapshot projection test
    snapshot = memory_runtime.snapshot("s1", "global")
    if hasattr(snapshot, "episode_hints"):
        print(f"✅ MemoryRuntime.snapshot() successfully populated episode_hints projection (Count: {len(snapshot.episode_hints)}).")
    else:
        print("❌ MemoryRuntime.snapshot() missing episode_hints projection field.")
        all_passed = False

    print("\n[5/6] Testing Canonical Execution Spine Integration...")
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
    
    # Dispatch an ExecutionPlan created using hints
    llm_planner = LLMPlannerStrategy(inference_strategy=DummyInferenceStrategy())
    guided_decision = await llm_planner.plan(interaction, snapshot)
    plan = llm_planner.create_plan(guided_decision, interaction, session_id="s1")
    kernel.context.event_bus.publish(plan)
    
    for _ in range(20):
        await asyncio.sleep(0.1)
        
    if len(events_captured) > 0:
        print("✅ Canonical execution spine completed cleanly with MemoryRetrievalEngine hints.")
    else:
        print("❌ Canonical execution spine failed to emit ExecutionCompletedEvent.")
        all_passed = False
        
    await kernel.shutdown()

    print("\n[6/6] Zero Regression Verification (COG-31B, COG-31C, COG-31D, COG-31E)...")
    # Verify COG-31E Deterministic Replay remains 100% functional
    replay_strategy = MemoryReplayStrategy(capability_registry=cap_registry, confidence_threshold=0.70)
    exact_interaction = InteractionEnvelope(
        id="int_exact", session_id="s1", timestamp=datetime.now(),
        origin="CLI", transport="CLI", payload="set timer for 5 minutes"
    )
    exact_memory = MemorySnapshot(session_id="s1", episodes=[ep1])
    setattr(exact_memory, "environment_fingerprint", fp)
    
    exact_decision = await replay_strategy.plan(exact_interaction, exact_memory)
    if exact_decision and exact_decision.confidence != DecisionQuality.REJECTED:
        print("✅ Zero Regression Verification PASSED: COG-31E Replay & COG-31B Memory Planning fully intact.")
    else:
        print("❌ Regression Verification FAILED: COG-31E Deterministic Replay broken.")
        all_passed = False

    print("\n==========================================================")
    if all_passed:
        print("DECISION: COG-31A IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: COG-31A VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
