import sys
import os
import time
import asyncio
from datetime import datetime

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.capability_contracts import SimpleCapabilityRegistry
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer

from desktop.models.environment import EnvironmentFingerprint
from desktop.models.memory import Episode, EpisodeScore, EpisodeQuality
from desktop.models.cognition import ExecutionPlan, WorkflowRequest, ExecutionPolicy, ApprovalRequirement
from desktop.models.execution import ExecutionTrace, ExecutionStep, ExecutionStatus
from desktop.runtimes.verification_runtime import VerificationResult, VerificationStatus
from desktop.runtimes.memory_runtime import MemoryRuntime

async def run_verification():
    print("==========================================================")
    print("Starting COG-31D Models & Persistence Verification")
    print("==========================================================\n")
    
    all_passed = True
    
    print("[1/5] Testing EnvironmentFingerprint Model & Serialization...")
    fp = EnvironmentFingerprint(
        fingerprint_id="fp_test_31d",
        os_platform="Windows 11",
        screen_resolution="1920x1080",
        active_window="VSCode",
        timestamp=time.time(),
        connected_monitors=["Monitor_1"],
        running_processes=["python.exe", "code.exe"]
    )
    fp_dict = fp.to_dict()
    fp_restored = EnvironmentFingerprint.from_dict(fp_dict)
    
    if fp_restored.fingerprint_id == fp.fingerprint_id and fp_restored.os_platform == fp.os_platform:
        print("✅ EnvironmentFingerprint serialization round-trip PASSED.")
    else:
        print("❌ EnvironmentFingerprint serialization round-trip FAILED.")
        all_passed = False

    print("\n[2/5] Testing EpisodeScore & EpisodeQuality Models & Serialization...")
    score = EpisodeScore(score=0.95, last_updated=time.time(), decay_factor=0.99)
    quality = EpisodeQuality(latency_ms=120.5, accuracy_confidence=0.98, user_feedback_score=5.0)
    
    score_dict = score.to_dict()
    score_restored = EpisodeScore.from_dict(score_dict)
    quality_dict = quality.to_dict()
    quality_restored = EpisodeQuality.from_dict(quality_dict)
    
    if score_restored.score == score.score and quality_restored.latency_ms == quality.latency_ms:
        print("✅ EpisodeScore & EpisodeQuality serialization round-trip PASSED.")
    else:
        print("❌ EpisodeScore & EpisodeQuality serialization round-trip FAILED.")
        all_passed = False

    print("\n[3/5] Testing Canonical Episode Model & Versioned Plan Serialization...")
    plan = ExecutionPlan(
        approval=ApprovalRequirement(required=False, reason="Test"),
        workflows=[
            WorkflowRequest(action="text_response", parameters={"text": "Test"}, policy=ExecutionPolicy(timeout=5.0), correlation_id="c1")
        ]
    )
    trace = ExecutionTrace(trace_id="tr_1", plan_id="p_1", total_duration_ms=150.0, overall_status=ExecutionStatus.SUCCESS)
    trace.steps.append(ExecutionStep(step_id="st_1", capability_name="text_response", status=ExecutionStatus.SUCCESS, start_time=time.time(), end_time=time.time()))
    v_res = VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=["Fallback"], strategy_used=None)
    
    episode = Episode(
        episode_id="ep_test_31d",
        intent={"subtype": "text_response", "query": "Hello CHITTI"},
        execution_plan=plan,
        execution_trace=trace,
        verification_result=v_res,
        fingerprint=fp,
        timestamp=time.time(),
        episode_score=score,
        episode_quality=quality
    )
    
    ep_dict = episode.to_dict()
    if ep_dict.get("execution_plan", {}).get("schema_version") == "1.0":
        print("✅ Versioned ExecutionPlan serialization (Rule 30) PASSED.")
    else:
        print("❌ Versioned ExecutionPlan serialization FAILED.")
        all_passed = False
        
    ep_restored = Episode.from_dict(ep_dict)
    if ep_restored.episode_id == episode.episode_id and ep_restored.fingerprint.os_platform == fp.os_platform:
        print("✅ Episode deserialization round-trip PASSED.")
    else:
        print("❌ Episode deserialization FAILED.")
        all_passed = False

    print("\n[4/5] Testing MemoryRuntime Phase 3 SQLite Persistence Round-Trip...")
    test_db = "storage/test_chitti_memory_31d.db"
    if os.path.exists(test_db):
        os.remove(test_db)
        
    mem_runtime = MemoryRuntime(db_path=test_db)
    mem_runtime._init_db()
    
    save_ok = mem_runtime.save_phase3_episode(episode)
    if save_ok:
        print("✅ save_phase3_episode() returned True.")
    else:
        print("❌ save_phase3_episode() returned False.")
        all_passed = False
        
    retrieved_ep = mem_runtime.get_phase3_episode("ep_test_31d")
    if retrieved_ep and retrieved_ep.episode_id == episode.episode_id:
        print("✅ get_phase3_episode() successfully retrieved episode with exact ID match.")
        
        # Field-by-Field Integrity Assertions
        check_id = (retrieved_ep.episode_id == episode.episode_id)
        check_intent = (retrieved_ep.intent == episode.intent)
        check_plan = (retrieved_ep.execution_plan == ep_dict["execution_plan"])
        check_trace = (retrieved_ep.execution_trace == ep_dict["execution_trace"])
        check_v_res = (retrieved_ep.verification_result == ep_dict["verification_result"])
        check_fp = (retrieved_ep.fingerprint.to_dict() == fp.to_dict())
        check_score = (retrieved_ep.episode_score.to_dict() == score.to_dict())
        check_quality = (retrieved_ep.episode_quality.to_dict() == quality.to_dict())
        check_version = (retrieved_ep.version == episode.version)
        
        if all([check_id, check_intent, check_plan, check_trace, check_v_res, check_fp, check_score, check_quality, check_version]):
            print("✅ All 9 Field-by-Field Persistence Round-Trip Assertions PASSED without data loss.")
        else:
            print(f"❌ Field-by-Field Integrity Check FAILED: id={check_id}, intent={check_intent}, plan={check_plan}, trace={check_trace}, v_res={check_v_res}, fp={check_fp}, score={check_score}, quality={check_quality}, version={check_version}")
            all_passed = False
    else:
        print("❌ get_phase3_episode() failed to retrieve episode.")
        all_passed = False
        
    try:
        if os.path.exists(test_db):
            os.remove(test_db)
    except Exception:
        pass

    print("\n[5/5] Testing BootManager Regression Boot...")
    config = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config)
    from desktop.runtimes.capability.registry import CapabilityRegistry
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    boot_ok = await boot.initialize()
    if boot_ok:
        kernel = await boot.start()
        print("✅ BootManager initialized and started cleanly in READY state.")
        await kernel.shutdown()
    else:
        print("❌ BootManager initialization failed.")
        all_passed = False

    print("\n==========================================================")
    if all_passed:
        print("DECISION: COG-31D IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: COG-31D VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
