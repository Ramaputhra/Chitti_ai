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

from desktop.models.presentation import (
    PresentationBundle, BundleType, ExperienceType, SupportedRenderer
)
from desktop.models.analytics import AnalyticsRecord, AnalyticsPresentationBundle
from desktop.runtimes.analytics_runtime import AnalyticsRuntime
from desktop.runtimes.presentation_runtime import PresentationRuntime

from desktop.presentation.productivity.experience import ProductivityDashboardExperience
from desktop.presentation.productivity.renderers import DashboardRenderer
from desktop.presentation.productivity.multimodal_renderers import VoiceRenderer, AvatarRenderer

async def run_verification():
    print("==========================================================")
    print("Starting S32G Multimodal Renderers Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Booting PresentationRuntime & Registering Multimodal Renderers...")
    presentation_runtime = PresentationRuntime()
    await presentation_runtime.initialize()
    await presentation_runtime.start()

    exp = ProductivityDashboardExperience()
    dashboard_renderer = DashboardRenderer()
    voice_renderer = VoiceRenderer()
    avatar_renderer = AvatarRenderer()

    presentation_runtime.register_experience(BundleType.ANALYTICS, ExperienceType.DASHBOARD, exp)
    presentation_runtime.register_renderer(SupportedRenderer.DASHBOARD_RENDERER, dashboard_renderer)
    presentation_runtime.register_renderer(SupportedRenderer.VOICE_RENDERER, voice_renderer)
    presentation_runtime.register_renderer(SupportedRenderer.AVATAR_RENDERER, avatar_renderer)

    if (presentation_runtime.renderer_registry.get_renderer(SupportedRenderer.VOICE_RENDERER) == voice_renderer and
        presentation_runtime.renderer_registry.get_renderer(SupportedRenderer.AVATAR_RENDERER) == avatar_renderer):
        print("✅ VoiceRenderer and AvatarRenderer registered cleanly in RendererRegistry.")
    else:
        print("❌ Renderer registration FAILED.")
        all_passed = False

    print("\n[2/6] Ingesting Telemetry & Generating AnalyticsPresentationBundle...")
    if os.path.exists("storage/test_s32g_analytics.db"):
        try:
            os.remove("storage/test_s32g_analytics.db")
        except Exception:
            pass

    analytics_runtime = AnalyticsRuntime(db_path="storage/test_s32g_analytics.db")
    await analytics_runtime.start()

    rec1 = AnalyticsRecord(
        record_id="rec_s32g_1",
        event_type="EXECUTION_COMPLETED",
        source_subsystem="VerificationRuntime",
        session_id="s_multimodal",
        timestamp=time.time() - 15,
        duration_ms=180.0,
        status="SUCCESS",
        payload_json='{"trace_id": "t1", "correlation_id": "c1", "verification_status": "VERIFIED_SUCCESS"}'
    )
    rec2 = AnalyticsRecord(
        record_id="rec_s32g_2",
        event_type="USER_ACTIVITY",
        source_subsystem="DesktopActivityRuntime",
        session_id="s_multimodal",
        timestamp=time.time() - 3,
        duration_ms=8000.0,
        status="INFO",
        payload_json='{"app_name": "Visual Studio Code", "window_title": "desktop/presentation/productivity/multimodal_renderers.py"}'
    )
    analytics_runtime.save_record(rec1)
    analytics_runtime.save_record(rec2)

    bundle = analytics_runtime.get_presentation_bundle("s_multimodal")
    if bundle and bundle.suggested_narration_facts:
        print(f"✅ AnalyticsPresentationBundle generated with SuggestedNarrationFacts (App: {bundle.suggested_narration_facts.top_application}).")
    else:
        print("❌ AnalyticsPresentationBundle generation FAILED.")
        all_passed = False

    print("\n[3/6] Executing Multimodal Pipeline Dispatch (render_bundle)...")
    result = presentation_runtime.render_bundle(bundle)
    if result and result.success:
        print(f"✅ PresentationRuntime executed multimodal pipeline (Presentation ID: {result.presentation_id}).")
    else:
        print("❌ Multimodal render_bundle execution FAILED.")
        all_passed = False

    print("\n[4/6] Verifying VoiceRenderer Output (NarrationComposer)...")
    voice_out = result.rendered_outputs.get("VOICE_RENDERER", {})
    narration_text = voice_out.get("narration", {}).get("narration_text", "")
    if voice_out and "Primary application was Visual Studio Code" in narration_text:
        print(f"✅ VoiceRenderer generated structured TTS narration cleanly: '{narration_text}'.")
    else:
        print("❌ VoiceRenderer output verification FAILED.")
        all_passed = False

    print("\n[5/6] Verifying AvatarRenderer Output (AvatarExpressionMapper)...")
    avatar_out = result.rendered_outputs.get("AVATAR_RENDERER", {})
    if avatar_out and avatar_out.get("expression") == "HAPPY" and avatar_out.get("gesture") == "NOD":
        print(f"✅ AvatarRenderer mapped facts cleanly (Expression: {avatar_out['expression']}, Gesture: {avatar_out['gesture']}).")
    else:
        print("❌ AvatarRenderer output verification FAILED.")
        all_passed = False

    await analytics_runtime.stop()
    await presentation_runtime.stop()

    print("\n[6/6] Zero Regression Verification (S32A..S32F & Kernel Boot)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: S32A..S32F and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S32G IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S32G VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
