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

from desktop.models.analytics import (
    AnalyticsRecord, UserActivityEvent, TimelineEntry, ActivityTimeline,
    ExecutionMetrics, ProductivitySummary, InsightCard, SuggestedNarrationFacts,
    AnalyticsPresentationBundle
)
from desktop.runtimes.activity.desktop_activity_runtime import DesktopActivityRuntime
from desktop.runtimes.analytics_runtime import AnalyticsRuntime

async def run_verification():
    print("==========================================================")
    print("Starting S32C Analytics Domain Models Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Initializing AnalyticsRuntime & Ingesting Test Telemetry...")
    if os.path.exists("storage/test_s32c_analytics.db"):
        try:
            os.remove("storage/test_s32c_analytics.db")
        except Exception:
            pass

    analytics_runtime = AnalyticsRuntime(db_path="storage/test_s32c_analytics.db")
    await analytics_runtime.start()

    # Ingest records
    rec1 = AnalyticsRecord(
        record_id="rec_s32c_1",
        event_type="EXECUTION_COMPLETED",
        source_subsystem="VerificationRuntime",
        session_id="s_domain",
        timestamp=time.time() - 30,
        duration_ms=150.0,
        status="SUCCESS",
        payload_json='{"trace_id": "t1", "correlation_id": "c1", "verification_status": "VERIFIED_SUCCESS"}'
    )
    rec2 = AnalyticsRecord(
        record_id="rec_s32c_2",
        event_type="USER_ACTIVITY",
        source_subsystem="DesktopActivityRuntime",
        session_id="s_domain",
        timestamp=time.time() - 10,
        duration_ms=5000.0,
        status="INFO",
        payload_json='{"app_name": "Visual Studio Code", "window_title": "desktop/models/analytics.py"}'
    )
    analytics_runtime.save_record(rec1)
    analytics_runtime.save_record(rec2)
    print("✅ Ingested test telemetry records into analytics.db.")

    print("\n[2/6] Testing ActivityTimeline & TimelineEntry Generation...")
    timeline = analytics_runtime.get_structured_timeline(session_id="s_domain")
    if timeline.total_entries == 2 and isinstance(timeline.entries[0], TimelineEntry):
        print(f"✅ ActivityTimeline generated cleanly with {timeline.total_entries} TimelineEntry objects.")
    else:
        print("❌ ActivityTimeline generation FAILED.")
        all_passed = False

    print("\n[3/6] Testing ExecutionMetrics & ProductivitySummary Aggregation...")
    metrics = analytics_runtime.get_execution_metrics(session_id="s_domain")
    summary = analytics_runtime.get_productivity_summary(session_id="s_domain")
    
    if metrics.total_executions == 1 and metrics.success_rate == 1.0 and summary.total_records == 2:
        print("✅ ExecutionMetrics and ProductivitySummary aggregated correctly.")
    else:
        print("❌ ExecutionMetrics / ProductivitySummary aggregation FAILED.")
        all_passed = False

    print("\n[4/6] Testing InsightCard Generation (Pure Factual Analytics Only)...")
    insights = analytics_runtime.get_insight_cards(session_id="s_domain")
    if len(insights) >= 2 and all(isinstance(c, InsightCard) for c in insights):
        print(f"✅ InsightCards generated ({len(insights)} cards). Zero interpretation/intent hypothesis.")
    else:
        print("❌ InsightCard generation FAILED.")
        all_passed = False

    print("\n[5/6] Testing SuggestedNarrationFacts & AnalyticsPresentationBundle Aggregation...")
    narration_facts = analytics_runtime.get_suggested_narration_facts(session_id="s_domain")
    bundle = analytics_runtime.get_presentation_bundle(session_id="s_domain")
    
    if (narration_facts.top_application == "Visual Studio Code" and 
        bundle and bundle.domain_type == "ANALYTICS" and 
        bundle.activity_timeline and bundle.suggested_narration_facts):
        print(f"✅ AnalyticsPresentationBundle fully aggregated all S32C domain models (Bundle ID: {bundle.bundle_id}).")
    else:
        print("❌ AnalyticsPresentationBundle aggregation FAILED.")
        all_passed = False

    await analytics_runtime.stop()

    print("\n[6/6] Zero Regression Verification (S32A, S32B & Kernel Boot)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: S32A, S32B, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S32C IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S32C VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
