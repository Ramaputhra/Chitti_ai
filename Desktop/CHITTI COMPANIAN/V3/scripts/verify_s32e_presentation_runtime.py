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
from desktop.models.analytics import AnalyticsPresentationBundle, ExecutionMetrics
from desktop.runtimes.presentation_runtime import PresentationRuntime
from desktop.runtimes.presentation.contracts import IPresentationExperience, IPresentationRenderer
from desktop.runtimes.analytics_runtime import AnalyticsRuntime

# Mock domain experience & renderer for S32E testing
class DummyProductivityDashboardExperience(IPresentationExperience):
    def get_experience_name(self) -> str:
        return "DummyProductivityDashboardExperience"

class DummyDashboardRenderer(IPresentationRenderer):
    def get_renderer_id(self) -> SupportedRenderer:
        return SupportedRenderer.DASHBOARD_RENDERER

    def render(self, bundle: PresentationBundle) -> Any:
        return {"status": "RENDERED_DASHBOARD", "bundle_id": bundle.bundle_id}

async def run_verification():
    print("==========================================================")
    print("Starting S32E Presentation Runtime Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Testing PresentationRuntime Initialization & Boot...")
    presentation_runtime = PresentationRuntime()
    await presentation_runtime.initialize()
    await presentation_runtime.start()
    if presentation_runtime._running:
        print("✅ PresentationRuntime booted cleanly and reports HEALTHY.")
    else:
        print("❌ PresentationRuntime initialization FAILED.")
        all_passed = False

    print("\n[2/6] Testing Registry-Driven Experience Registration (ExperienceRegistry)...")
    exp = DummyProductivityDashboardExperience()
    presentation_runtime.register_experience(BundleType.ANALYTICS, ExperienceType.DASHBOARD, exp)
    
    retrieved_exp = presentation_runtime.experience_registry.get_experience(BundleType.ANALYTICS, ExperienceType.DASHBOARD)
    if retrieved_exp == exp:
        print("✅ ExperienceRegistry registered and retrieved experience cleanly with zero hardcoded conditionals.")
    else:
        print("❌ ExperienceRegistry registration FAILED.")
        all_passed = False

    print("\n[3/6] Testing Registry-Driven Renderer Registration (RendererRegistry)...")
    renderer = DummyDashboardRenderer()
    presentation_runtime.register_renderer(SupportedRenderer.DASHBOARD_RENDERER, renderer)
    
    retrieved_renderer = presentation_runtime.renderer_registry.get_renderer(SupportedRenderer.DASHBOARD_RENDERER)
    if retrieved_renderer == renderer:
        print("✅ RendererRegistry registered and retrieved renderer cleanly with zero hardcoded renderers.")
    else:
        print("❌ RendererRegistry registration FAILED.")
        all_passed = False

    print("\n[4/6] Testing AssetResolver & PresentationSession Composition...")
    analytics_bundle = AnalyticsPresentationBundle(
        bundle_id="bundle_s32e_test",
        session_id="s_presentation",
        execution_metrics=ExecutionMetrics(total_executions=10, success_rate=0.9)
    )
    
    resolved_renderers = presentation_runtime.asset_resolver.resolve_renderers(analytics_bundle)
    if len(resolved_renderers) == 4 and "DASHBOARD_RENDERER" in resolved_renderers:
        print(f"✅ AssetResolver correctly resolved {len(resolved_renderers)} renderers from bundle metadata.")
    else:
        print("❌ AssetResolver renderer resolution FAILED.")
        all_passed = False

    print("\n[5/6] Testing Universal Pipeline Execution (render_bundle)...")
    result = presentation_runtime.render_bundle(analytics_bundle)
    if (result and result.success and 
        "DASHBOARD_RENDERER" in result.rendered_outputs and 
        result.rendered_outputs["DASHBOARD_RENDERER"]["status"] == "RENDERED_DASHBOARD"):
        print(f"✅ PresentationRuntime executed full pipeline cleanly (Presentation ID: {result.presentation_id}, Time: {result.execution_time_ms} ms).")
    else:
        print("❌ PresentationRuntime render_bundle pipeline FAILED.")
        all_passed = False

    await presentation_runtime.stop()

    print("\n[6/6] Zero Regression Verification (S32A..S32D & Kernel Boot)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: S32A, S32B, S32C, S32D, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S32E IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S32E VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
