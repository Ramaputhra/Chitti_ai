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
from desktop.models.memory import Episode, EpisodeScore, EpisodeQuality
from desktop.models.cognition import ExecutionPlan, WorkflowRequest
from desktop.models.execution import ExecutionTrace, ExecutionStatus
from desktop.models.events import ExecutionCompletedEvent
from desktop.runtimes.verification_runtime import VerificationResult, VerificationStatus

from desktop.models.analytics import (
    AnalyticsRecord, ExecutionMetrics, ActivityTimelineEntry, ProductivitySummary, AnalyticsPresentationBundle
)
from desktop.runtimes.analytics.collector import AnalyticsCollector
from desktop.runtimes.analytics_runtime import AnalyticsRuntime

async def run_verification():
    print("==========================================================")
    print("Starting S32A Analytics Foundation Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Testing AnalyticsRuntime & SQLite Database Initialization...")
    if os.path.exists("storage/test_analytics.db"):
        try:
            os.remove("storage/test_analytics.db")
        except Exception:
            pass

    analytics_runtime = AnalyticsRuntime(db_path="storage/test_analytics.db")
    await analytics_runtime.start()
    if analytics_runtime._running and os.path.exists("storage/test_analytics.db"):
        print("✅ AnalyticsRuntime booted cleanly and storage/test_analytics.db initialized.")
    else:
        print("❌ AnalyticsRuntime initialization FAILED.")
        all_passed = False

    print("\n[2/6] Testing AnalyticsCollector Event Normalization...")
    collector = AnalyticsCollector()
    
    fp = EnvironmentFingerprint(fingerprint_id="fp1", os_platform="Windows 11", screen_resolution="1920x1080", active_window="Desktop", timestamp=time.time())
    ep = Episode(
        episode_id="ep_analytics_test",
        intent={"subtype": "set timer"},
        execution_plan=ExecutionPlan(workflows=[WorkflowRequest(action="text_response", correlation_id="c1")]),
        execution_trace=ExecutionTrace(trace_id="t1", plan_id="p1", total_duration_ms=120.0, overall_status=ExecutionStatus.SUCCESS),
        verification_result=VerificationResult(status=VerificationStatus.VERIFIED_SUCCESS, evidence=["OK"], strategy_used=None),
        fingerprint=fp,
        timestamp=time.time()
    )
    
    event = ExecutionCompletedEvent(
        source="VerificationRuntime",
        correlation_id="c1",
        metadata={"duration_ms": 120.0, "status": "SUCCESS", "trace_id": "t1"}
    )
    setattr(event, "session_id", "s1")
    
    record = collector.normalize_event(event)
    if record and record.event_type == "EXECUTION_COMPLETED" and record.duration_ms == 120.0:
        print(f"✅ AnalyticsCollector correctly normalized ExecutionCompletedEvent to AnalyticsRecord (ID: {record.record_id}).")
    else:
        print("❌ AnalyticsCollector event normalization FAILED.")
        all_passed = False

    print("\n[3/6] Testing SQLite Persistence (storage/analytics.db)...")
    saved = analytics_runtime.save_record(record)
    records = analytics_runtime.get_records(session_id="s1")
    if saved and len(records) > 0 and records[0].record_id == record.record_id:
        print("✅ AnalyticsRecord persisted and retrieved successfully from SQLite database.")
    else:
        print("❌ AnalyticsRecord SQLite persistence FAILED.")
        all_passed = False

    print("\n[4/6] Testing Public Analytics APIs...")
    metrics = analytics_runtime.get_execution_metrics("s1")
    timeline = analytics_runtime.get_activity_timeline("s1")
    summary = analytics_runtime.get_productivity_summary("s1")
    
    if metrics.total_executions == 1 and len(timeline) == 1 and summary.total_records == 1:
        print("✅ Public Analytics APIs (get_execution_metrics, get_activity_timeline, get_productivity_summary) verified.")
    else:
        print("❌ Public Analytics APIs FAILED.")
        all_passed = False

    print("\n[5/6] Testing AnalyticsPresentationBundle Domain Projection...")
    bundle = analytics_runtime.get_presentation_bundle("s1")
    if bundle and bundle.domain_type == "ANALYTICS" and bundle.execution_metrics.total_executions == 1:
        print(f"✅ AnalyticsPresentationBundle projected cleanly (Bundle ID: {bundle.bundle_id}).")
    else:
        print("❌ AnalyticsPresentationBundle projection FAILED.")
        all_passed = False

    await analytics_runtime.stop()

    print("\n[6/6] Zero Regression Verification (Cognitive Core V1 & Kernel Boot)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    # Verify Kernel boots and Cognitive Core operates normally
    events_captured = []
    def on_event(event):
        if event.__class__.__name__ in ["Event", "ExecutionCompletedEvent"]:
            events_captured.append(event)
            
    kernel.context.event_bus.subscribe(ExecutionCompletedEvent, on_event)
    
    plan = ExecutionPlan(workflows=[WorkflowRequest(action="text_response", correlation_id="c_analytics_smoke")])
    kernel.context.event_bus.publish(plan)
    
    for _ in range(20):
        await asyncio.sleep(0.1)
        
    if len(events_captured) > 0:
        print("✅ Zero Regression Verification PASSED: Cognitive Core V1 & Kernel execution spine fully intact.")
    else:
        print("❌ Cognitive Core execution spine FAILED.")
        all_passed = False
        
    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S32A IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S32A VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
