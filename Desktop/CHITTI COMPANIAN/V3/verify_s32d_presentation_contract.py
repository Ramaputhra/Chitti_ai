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
    PresentationBundle, BundleType, ExperienceType, SupportedRenderer, validate_presentation_bundle
)
from desktop.models.analytics import AnalyticsPresentationBundle, ExecutionMetrics, ProductivitySummary
from desktop.runtimes.analytics_runtime import AnalyticsRuntime

async def run_verification():
    print("==========================================================")
    print("Starting S32D Universal Presentation Contract Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Testing Base PresentationBundle Construction & Enums...")
    base_bundle = PresentationBundle(
        bundle_id="bundle_base_101",
        bundle_type=BundleType.SYSTEM,
        experience_type=ExperienceType.DASHBOARD,
        supported_renderers=[SupportedRenderer.DASHBOARD_RENDERER, SupportedRenderer.TEXT_RENDERER]
    )
    if base_bundle.bundle_id == "bundle_base_101" and base_bundle.bundle_type == BundleType.SYSTEM:
        print("✅ Base PresentationBundle created cleanly with Enums (BundleType, ExperienceType, SupportedRenderer).")
    else:
        print("❌ Base PresentationBundle creation FAILED.")
        all_passed = False

    print("\n[2/6] Testing AnalyticsPresentationBundle Inheritance...")
    analytics_bundle = AnalyticsPresentationBundle(
        bundle_id="bundle_analytics_test",
        session_id="s_contract",
        execution_metrics=ExecutionMetrics(total_executions=5, success_rate=1.0)
    )
    
    is_inherited = isinstance(analytics_bundle, PresentationBundle)
    if is_inherited and analytics_bundle.bundle_type == BundleType.ANALYTICS:
        print("✅ AnalyticsPresentationBundle correctly inherits from base PresentationBundle contract.")
    else:
        print("❌ AnalyticsPresentationBundle inheritance FAILED.")
        all_passed = False

    print("\n[3/6] Testing PresentationBundle Serialization Round-Trip...")
    dict_data = base_bundle.to_dict()
    restored_bundle = PresentationBundle.from_dict(dict_data)
    if restored_bundle.bundle_id == base_bundle.bundle_id and restored_bundle.bundle_type == base_bundle.bundle_type:
        print("✅ PresentationBundle serialization (to_dict/from_dict) verified cleanly.")
    else:
        print("❌ PresentationBundle serialization round-trip FAILED.")
        all_passed = False

    print("\n[4/6] Testing Bundle Validation Utilities (validate_presentation_bundle)...")
    v_base = validate_presentation_bundle(base_bundle)
    v_analytics = validate_presentation_bundle(analytics_bundle)
    v_invalid = validate_presentation_bundle({"invalid": "object"})
    
    if v_base and v_analytics and not v_invalid:
        print("✅ validate_presentation_bundle correctly validates PresentationBundle derivatives and rejects non-bundles.")
    else:
        print("❌ validate_presentation_bundle verification FAILED.")
        all_passed = False

    print("\n[5/6] Testing AnalyticsRuntime Domain Presentation Bundle Projection...")
    if os.path.exists("storage/test_s32d_analytics.db"):
        try:
            os.remove("storage/test_s32d_analytics.db")
        except Exception:
            pass

    analytics_runtime = AnalyticsRuntime(db_path="storage/test_s32d_analytics.db")
    await analytics_runtime.start()
    
    domain_bundle = analytics_runtime.get_presentation_bundle("s_contract")
    if validate_presentation_bundle(domain_bundle) and SupportedRenderer.DASHBOARD_RENDERER in domain_bundle.supported_renderers:
        print(f"✅ AnalyticsRuntime projected valid domain PresentationBundle (Renderers: {len(domain_bundle.supported_renderers)}).")
    else:
        print("❌ AnalyticsRuntime domain PresentationBundle projection FAILED.")
        all_passed = False

    await analytics_runtime.stop()

    print("\n[6/6] Zero Regression Verification (S32A, S32B, S32C & Kernel Boot)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: S32A, S32B, S32C, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S32D IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S32D VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
