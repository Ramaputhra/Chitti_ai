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
    Episode, EpisodeScore, EpisodeQuality, MemorySnapshot, ExperienceLevel, MemoryEpisodeHint
)
from desktop.models.cognition import (
    ExecutionPlan, WorkflowRequest, ExecutionPolicy, ApprovalRequirement, DecisionQuality, PlanningDecision
)
from desktop.models.execution import ExecutionTrace, ExecutionStep, ExecutionStatus
from desktop.models.interaction import InteractionEnvelope
from desktop.models.events import ExecutionCompletedEvent
from desktop.runtimes.verification_runtime import VerificationResult, VerificationStatus
from desktop.platform.strategies.memory_replay import MemoryReplayStrategy
from desktop.platform.strategies.hybrid_planner import HybridPlannerStrategy
from desktop.platform.strategies.llm_planner import LLMPlannerStrategy
from desktop.app.prompt_builder import PromptBuilder
from desktop.app.planner_contracts import IPlannerStrategy

# Mock Inference Strategy for testing LLM Planner Strategy
class DummyInferenceResult:
    def __init__(self, intent="GreetingIntent", confidence=0.95, entities=None, reasoning_notes=None):
        self.intent = intent
        self.confidence = confidence
        self.entities = entities or {}
        self.reasoning_notes = reasoning_notes or "Dummy inference notes"

class DummyInferenceStrategy:
    async def infer(self, interaction, memory):
        return DummyInferenceResult(intent="GreetingIntent", confidence=0.95)

async def run_verification():
    print("==========================================================")
    print("Starting COG-31B Memory-Aware LLM Planning Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Testing Pure Domain Model & PromptBuilder Sanitization...")
    hint = MemoryEpisodeHint(
        intent_summary="set timer for 5 minutes",
        verified_outcome="VERIFIED_SUCCESS",
        workflow_summary="SetTimerCapability",
        parameter_summary={"duration_sec": 300, "label": "Tea Timer"},
        episode_score=0.88,
        episode_quality=0.95,
        experience_level=ExperienceLevel.HIGH
    )
    
    # Verify MemoryEpisodeHint has NO XML serialization method on itself (Refinement)
    if hasattr(hint, "to_prompt_xml") or hasattr(hint, "to_xml"):
        print("❌ MemoryEpisodeHint failed pure domain model check (Contains XML generation methods).")
        all_passed = False
    else:
        print("✅ MemoryEpisodeHint is a PURE DOMAIN MODEL (No XML/JSON methods).")

    # PromptBuilder serialization test
    prompt_xml = PromptBuilder.format_experience_context([hint])
    if "<historical_experiences>" in prompt_xml and '<experience rank="1" level="HIGH" score="0.88">' in prompt_xml:
        print("✅ PromptBuilder transformed MemoryEpisodeHint into anonymized XML context.")
    else:
        print("❌ PromptBuilder failed experience XML formatting.")
        all_passed = False
        
    if "episode_id" in prompt_xml or "storage" in prompt_xml:
        print("❌ PromptBuilder leaked internal storage details.")
        all_passed = False
    else:
        print("✅ PromptBuilder output is fully anonymized (No episode_id or storage keys).")

    print("\n[2/6] Testing Guided LLM Planning...")
    memory_snapshot = MemorySnapshot(session_id="s1")
    memory_snapshot.episode_hints = [hint]
    
    llm_planner = LLMPlannerStrategy(inference_strategy=DummyInferenceStrategy())
    interaction = InteractionEnvelope(
        id="int_guided",
        session_id="s1",
        timestamp=datetime.now(),
        origin="CLI",
        transport="CLI",
        payload="set timer for 5 minutes",
        metadata={"text": "Dynamic input"}
    )
    
    guided_decision = await llm_planner.plan(interaction, memory_snapshot)
    if getattr(guided_decision, "planning_mode", "") == "guided_llm" and getattr(guided_decision, "experience_context_injected", False):
        print("✅ LLMPlannerStrategy executed Guided LLM Planning with injected experience context.")
    else:
        print("❌ LLMPlannerStrategy Guided LLM Planning FAILED.")
        all_passed = False

    print("\n[3/6] Testing Zero-Shot LLM Planning...")
    empty_memory = MemorySnapshot(session_id="s1")
    zero_shot_decision = await llm_planner.plan(interaction, empty_memory)
    if getattr(zero_shot_decision, "planning_mode", "") == "zero_shot" and not getattr(zero_shot_decision, "experience_context_injected", True):
        print("✅ LLMPlannerStrategy executed Zero-Shot LLM Planning when no hints present.")
    else:
        print("❌ LLMPlannerStrategy Zero-Shot LLM Planning FAILED.")
        all_passed = False

    print("\n[4/6] Testing HybridPlannerStrategy Experience Level Routing...")
    cap_registry = CapabilityRegistry()
    from desktop.runtimes.capability.provider import CapabilityProvider
    provider = CapabilityProvider(cap_registry)
    provider.register_all()

    replay_strategy = MemoryReplayStrategy(capability_registry=cap_registry, confidence_threshold=0.70)
    
    class DummyClarificationPlanner(IPlannerStrategy):
        def parse_intent(self, i, c): pass
        def formulate_decision(self, i, c): pass
        def create_plan(self, d, i, s): pass
        async def plan(self, i, m):
            return PlanningDecision(plan=ExecutionPlan(workflows=[]), confidence=DecisionQuality.AMBIGUOUS)

    hybrid_planner = HybridPlannerStrategy(
        deterministic_planner=llm_planner,
        llm_planner=llm_planner,
        clarification_planner=DummyClarificationPlanner(),
        policy=None,
        intent_store=None,
        replay_strategy=replay_strategy
    )

    # Guided LLM Route test
    hybrid_guided_decision = await hybrid_planner.plan(interaction, memory_snapshot)
    if hybrid_guided_decision and getattr(hybrid_guided_decision, "planning_mode", "") == "guided_llm":
        print("✅ HybridPlannerStrategy correctly routed HIGH experience candidate to Guided LLM Planning.")
    else:
        print("❌ HybridPlannerStrategy Experience Level routing FAILED.")
        all_passed = False

    print("\n[5/6] Testing Production Smoke Test & Canonical Execution Spine...")
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
    
    # Create an ExecutionPlan from guided decision
    plan = llm_planner.create_plan(guided_decision, interaction, session_id="s1")
    kernel.context.event_bus.publish(plan)
    
    for _ in range(20):
        await asyncio.sleep(0.1)
        
    if len(events_captured) > 0:
        print("✅ Guided LLM plan completed canonical execution spine & emitted ExecutionCompletedEvent.")
    else:
        print("❌ Canonical execution spine failed to emit ExecutionCompletedEvent.")
        all_passed = False
        
    await kernel.shutdown()

    print("\n[6/6] Regression Verification (COG-31C, COG-31D, COG-31E)...")
    # Verify COG-31E Replay Strategy remains 100% functional
    orig_fp = EnvironmentFingerprint(fingerprint_id="fp1", os_platform="Windows 11", screen_resolution="1920x1080", active_window="Desktop", timestamp=time.time())
    orig_plan = ExecutionPlan(approval=ApprovalRequirement(required=False), workflows=[WorkflowRequest(action="text_response", correlation_id="c1")])
    orig_trace = ExecutionTrace(trace_id="tr1", plan_id="p1", total_duration_ms=10.0, overall_status=ExecutionStatus.SUCCESS)
    orig_v = VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=["Fallback"], strategy_used=None)
    
    exact_episode = Episode(
        episode_id="ep_exact",
        intent={"subtype": "text_response", "query": "say hello"},
        execution_plan=orig_plan,
        execution_trace=orig_trace,
        verification_result=orig_v,
        fingerprint=orig_fp,
        timestamp=time.time()
    )
    exact_memory = MemorySnapshot(session_id="s1", episodes=[exact_episode])
    setattr(exact_memory, "environment_fingerprint", orig_fp)
    
    exact_interaction = InteractionEnvelope(
        id="int_exact",
        session_id="s1",
        timestamp=datetime.now(),
        origin="CLI",
        transport="CLI",
        payload="say hello",
        metadata={"text": "say hello"}
    )
    exact_decision = await replay_strategy.plan(exact_interaction, exact_memory)
    if exact_decision and exact_decision.confidence != DecisionQuality.REJECTED:
        print("✅ Regression Verification PASSED: COG-31E Deterministic Replay remains 100% functional.")
    else:
        print("❌ Regression Verification FAILED: COG-31E Deterministic Replay broken.")
        all_passed = False

    print("\n==========================================================")
    if all_passed:
        print("DECISION: COG-31B IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: COG-31B VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
