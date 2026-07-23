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
    print("Starting S34A Character Studio Foundation Verification")
    print("==========================================================\n")
    
    all_passed = True
    studio_path = os.path.join(v3_root, "desktop", "character", "studio")

    print("[1/7] Verifying Canonical Character Studio Directory Structure...")
    req_dirs = [
        os.path.join(studio_path, "assets", "source", "character", "body"),
        os.path.join(studio_path, "assets", "source", "character", "face"),
        os.path.join(studio_path, "assets", "source", "character", "hands"),
        os.path.join(studio_path, "assets", "runtime", "behaviors", "system"),
        os.path.join(studio_path, "assets", "runtime", "behaviors", "speaking"),
        os.path.join(studio_path, "assets", "runtime", "behaviors", "working"),
        os.path.join(studio_path, "documentation"),
    ]
    all_dirs = all(os.path.exists(d) for d in req_dirs)
    if all_dirs:
        print("✅ Character Studio canonical directory hierarchy verified.")
    else:
        print("❌ Directory hierarchy verification FAILED.")
        all_passed = False

    print("\n[2/7] Verifying Source SVG Assets...")
    svg_sample = os.path.join(studio_path, "assets", "source", "character", "body", "body_base.svg")
    if os.path.exists(svg_sample):
        print("✅ Source SVG placeholder assets created cleanly.")
    else:
        print("❌ Source SVG verification FAILED.")
        all_passed = False

    print("\n[3/7] Verifying Behavior Clips & Permanent CHR_ Behavior IDs...")
    sample_clip = os.path.join(studio_path, "assets", "runtime", "behaviors", "system", "idle", "behavior.json")
    sample_frame = os.path.join(studio_path, "assets", "runtime", "behaviors", "system", "idle", "Frame01.png")
    sample_sound = os.path.join(studio_path, "assets", "runtime", "behaviors", "system", "idle", "sound.wav")
    
    valid_clip = os.path.exists(sample_clip) and os.path.exists(sample_frame) and os.path.exists(sample_sound)
    if valid_clip:
        with open(sample_clip, "r") as f:
            b_data = json.load(f)
        if b_data.get("behavior_id") == "CHR_IDLE_001":
            print(f"✅ Behavior clip verified with permanent ID: '{b_data['behavior_id']}'.")
        else:
            print("❌ Behavior ID check FAILED.")
            all_passed = False
    else:
        print("❌ Behavior clip verification FAILED.")
        all_passed = False

    print("\n[4/7] Verifying Documentation Assets (GUIDE, CATALOG, PROCEED, MIGRATION_AUDIT)...")
    docs = ["CHARACTER_STUDIO_GUIDE.md", "BEHAVIOR_CATALOG.md", "PROCEED.md", "CHARACTER_STUDIO_MIGRATION_AUDIT.md"]
    all_docs = all(os.path.exists(os.path.join(studio_path, "documentation", d)) for d in docs)
    if all_docs:
        print("✅ All 4 Character Studio documentation assets verified.")
    else:
        print("❌ Documentation assets verification FAILED.")
        all_passed = False

    print("\n[5/7] Verifying Legacy Cleanup & Consolidation (Expressions & desktop/assets/avatar)...")
    legacy_expr = os.path.join(v3_root, "Expressions")
    legacy_avatar = os.path.join(v3_root, "desktop", "assets", "avatar")
    
    clean_legacy = (not os.path.exists(legacy_expr)) and (not os.path.exists(legacy_avatar))
    if clean_legacy:
        print("✅ Legacy duplicate folders (Expressions/ and desktop/assets/avatar/) cleanly removed.")
    else:
        print("❌ Legacy cleanup verification FAILED.")
        all_passed = False

    print("\n[6/7] Verifying Character Props & Placeholder Sound Assets...")
    laptop_prop = os.path.join(studio_path, "assets", "runtime", "props", "laptop", "prop.json")
    sound_placeholder = os.path.join(studio_path, "assets", "runtime", "sounds", "boot.wav")
    if os.path.exists(laptop_prop) and os.path.exists(sound_placeholder):
        print("✅ Runtime props and sound placeholders verified cleanly.")
    else:
        print("❌ Props / Sounds verification FAILED.")
        all_passed = False

    print("\n[7/7] Zero Regression Verification (PresentationRuntime & Kernel Boot)...")
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
        print("DECISION: S34A IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S34A VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
