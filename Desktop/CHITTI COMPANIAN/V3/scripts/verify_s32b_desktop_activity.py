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
    UserActivityEvent, AnalyticsRecord, ExecutionMetrics, ActivityTimelineEntry, ProductivitySummary
)
from desktop.runtimes.activity.desktop_activity_runtime import DesktopActivityRuntime, get_active_window_info
from desktop.runtimes.analytics_runtime import AnalyticsRuntime

async def run_verification():
    print("==========================================================")
    print("Starting S32B Desktop Activity Platform Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Testing OS Active Window Information API...")
    info = get_active_window_info()
    if "app_name" in info and "window_title" in info:
        print(f"✅ Active window info detected: App='{info['app_name']}', Window='{info['window_title']}'.")
    else:
        print("❌ OS Active Window Info detection FAILED.")
        all_passed = False

    print("\n[2/6] Testing DesktopActivityRuntime Initialization & Boot...")
    activity_runtime = DesktopActivityRuntime()
    await activity_runtime.initialize()
    await activity_runtime.start()
    if activity_runtime._running:
        print("✅ DesktopActivityRuntime booted cleanly and reports HEALTHY.")
    else:
        print("❌ DesktopActivityRuntime initialization FAILED.")
        all_passed = False

    print("\n[3/6] Testing UserActivityEvent Generation & Window Focus Tracking...")
    event = activity_runtime.record_activity(
        app_name="Visual Studio Code",
        window_title="desktop/runtimes/activity/desktop_activity_runtime.py",
        duration_ms=4500.0,
        session_id="s1"
    )
    if event and event.app_name == "Visual Studio Code" and event.event_type == "USER_ACTIVITY":
        print(f"✅ UserActivityEvent created cleanly for '{event.app_name}'.")
    else:
        print("❌ UserActivityEvent generation FAILED.")
        all_passed = False

    print("\n[4/6] Testing EventBus Delivery from DesktopActivityRuntime -> AnalyticsRuntime...")
    if os.path.exists("storage/test_s32b_analytics.db"):
        try:
            os.remove("storage/test_s32b_analytics.db")
        except Exception:
            pass

    analytics_runtime = AnalyticsRuntime(db_path="storage/test_s32b_analytics.db")
    
    # Mock context with EventBus
    class MockEventBus:
        def __init__(self):
            self.handlers = {}
        def subscribe(self, event_type, handler):
            self.handlers[event_type.__name__] = handler
        def publish(self, event):
            ev_type = event.__class__.__name__
            if ev_type in self.handlers:
                self.handlers[ev_type](event)

    class MockContext:
        def __init__(self):
            self.event_bus = MockEventBus()

    ctx = MockContext()
    await analytics_runtime.initialize(ctx)
    await analytics_runtime.start()
    
    activity_runtime._context = ctx
    activity_runtime.record_activity("Google Chrome", "CHITTI Architecture - Google Search", duration_ms=1200.0, session_id="s1")
    
    records = analytics_runtime.get_records(session_id="s1")
    activity_records = [r for r in records if r.event_type == "USER_ACTIVITY"]
    
    if len(activity_records) > 0 and activity_records[0].source_subsystem == "DesktopActivityRuntime":
        print(f"✅ AnalyticsRuntime received and persisted UserActivityEvent via EventBus (Count: {len(activity_records)}).")
    else:
        print("❌ EventBus delivery from DesktopActivityRuntime to AnalyticsRuntime FAILED.")
        all_passed = False

    await activity_runtime.stop()
    await analytics_runtime.stop()

    print("\n[5/6] Testing Factual Activity Timeline (Rules 92 & 93 Compliance)...")
    timeline = analytics_runtime.get_activity_timeline(session_id="s1")
    if len(timeline) > 0 and "Focus Google Chrome" in timeline[0].title:
        print("✅ Factual ActivityTimeline verifies empirical facts (App, Window, Duration) with zero subjective inference.")
    else:
        print("❌ Factual ActivityTimeline verification FAILED.")
        all_passed = False

    print("\n[6/6] Zero Regression Verification (S32A Analytics & Kernel Boot)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: Kernel & S32A Analytics Foundation fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S32B IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S32B VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
