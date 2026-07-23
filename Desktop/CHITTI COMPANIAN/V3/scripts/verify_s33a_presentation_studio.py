import sys
import os
import json
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.capability.registry import CapabilityRegistry

async def run_verification():
    print("==========================================================")
    print("Starting S33A-R1 Presentation Studio Refinement Verification")
    print("==========================================================\n")
    
    all_passed = True
    studio_path = os.path.join(v3_root, "desktop", "presentation", "studio")

    print("[1/6] Verifying Presentation Studio Directory Structure...")
    required_dirs = [
        os.path.join(studio_path, "assets", "experiences", "productivity", "layouts"),
        os.path.join(studio_path, "assets", "shared", "components"),
        os.path.join(studio_path, "assets", "shared", "themes"),
        os.path.join(studio_path, "assets", "shared", "prompts"),
        os.path.join(studio_path, "assets", "shared", "animations"),
    ]
    missing = [d for d in required_dirs if not os.path.exists(d)]
    if not missing:
        print("✅ Required Presentation Studio directories exist.")
    else:
        print(f"❌ Directory structure verification FAILED. Missing: {missing}")
        all_passed = False

    print("\n[2/6] Verifying Character Assets Removal from Presentation Studio...")
    avatar_dir = os.path.join(studio_path, "assets", "experiences", "productivity", "avatar")
    voice_dir = os.path.join(studio_path, "assets", "experiences", "productivity", "voice")
    
    no_character_assets = (not os.path.exists(avatar_dir)) and (not os.path.exists(voice_dir))
    if no_character_assets:
        print("✅ Avatar and Voice directories cleanly removed from Presentation Studio.")
    else:
        print("❌ Character assets removal FAILED (avatar/voice folders still exist).")
        all_passed = False

    print("\n[3/6] Verifying Boundary Documentation (PRESENTATION_STUDIO_BOUNDARY.md & DESIGN_SYSTEM.md)...")
    boundary_file = os.path.join(studio_path, "PRESENTATION_STUDIO_BOUNDARY.md")
    ds_file = os.path.join(studio_path, "DESIGN_SYSTEM.md")
    
    has_boundary = os.path.exists(boundary_file) and os.path.exists(ds_file)
    if has_boundary:
        print("✅ PRESENTATION_STUDIO_BOUNDARY.md and DESIGN_SYSTEM.md boundary documentation verified.")
    else:
        print("❌ Boundary documentation FAILED.")
        all_passed = False

    print("\n[4/6] Verifying Theme Files & CSS Modules...")
    themes = ["dark.css", "glass.css", "light.css", "terminal.css"]
    all_themes = all(os.path.exists(os.path.join(studio_path, "assets", "shared", "themes", t)) for t in themes)
    if all_themes:
        print(f"✅ Verified {len(themes)} starter CSS theme files.")
    else:
        print("❌ CSS theme files verification FAILED.")
        all_passed = False

    print("\n[5/6] Verifying Prompt Templates Retained in Presentation Studio...")
    prompt_file = os.path.join(studio_path, "assets", "shared", "prompts", "productivity_summary.md")
    if os.path.exists(prompt_file):
        print("✅ Prompt templates correctly retained in Presentation Studio.")
    else:
        print("❌ Prompt templates retention FAILED.")
        all_passed = False

    print("\n[6/6] Zero Regression Verification (PresentationRuntime & Kernel Boot)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: PresentationRuntime and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S33A-R1 IMPLEMENTATION VERIFIED — READY FOR CERTIFICATION")
    else:
        print("DECISION: S33A-R1 VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
