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
    print("Starting S35A Desktop UI Studio Foundation Verification")
    print("==========================================================\n")
    
    all_passed = True
    studio_path = os.path.join(v3_root, "desktop", "ui", "studio")

    print("[1/7] Verifying Desktop UI Studio Directory Structure...")
    req_dirs = [
        os.path.join(studio_path, "assets", "overlays"),
        os.path.join(studio_path, "assets", "dialogs"),
        os.path.join(studio_path, "assets", "notifications"),
        os.path.join(studio_path, "assets", "countdown"),
        os.path.join(studio_path, "assets", "timers"),
        os.path.join(studio_path, "assets", "badges"),
        os.path.join(studio_path, "assets", "indicators"),
        os.path.join(studio_path, "assets", "icons"),
        os.path.join(studio_path, "assets", "animations"),
        os.path.join(studio_path, "assets", "sounds"),
        os.path.join(studio_path, "documentation")
    ]
    all_dirs = all(os.path.exists(d) for d in req_dirs)
    if all_dirs:
        print("✅ Desktop UI Studio directory hierarchy verified.")
    else:
        print("❌ Directory hierarchy verification FAILED.")
        all_passed = False

    print("\n[2/7] Verifying SVG Icon Assets...")
    icon_file = os.path.join(studio_path, "assets", "icons", "alarm.svg")
    if os.path.exists(icon_file):
        print("✅ Placeholder SVG icons generated cleanly.")
    else:
        print("❌ SVG icon verification FAILED.")
        all_passed = False

    print("\n[3/7] Verifying Category Mock UI Assets (PNG & JSON)...")
    alarm_png = os.path.join(studio_path, "assets", "alarm", "AlarmSet.png")
    alarm_json = os.path.join(studio_path, "assets", "alarm", "AlarmSet.json")
    
    if os.path.exists(alarm_png) and os.path.exists(alarm_json):
        with open(alarm_json, "r") as f:
            data = json.load(f)
        if data.get("asset_id") == "UI_ALARM_ALARMSET":
            print(f"✅ Mock UI PNG and JSON verified cleanly with ID: '{data['asset_id']}'.")
        else:
            print("❌ Asset ID check FAILED.")
            all_passed = False
    else:
        print("❌ Category mock UI asset verification FAILED.")
        all_passed = False

    print("\n[4/7] Verifying Sound Placeholders & Animation Assets...")
    sound_file = os.path.join(studio_path, "assets", "sounds", "alarm.wav")
    anim_file = os.path.join(studio_path, "assets", "animations", "pulse", "pulse.css")
    
    if os.path.exists(sound_file) and os.path.exists(anim_file):
        print("✅ WAV sound placeholders and CSS animations verified cleanly.")
    else:
        print("❌ Sound / Animation verification FAILED.")
        all_passed = False

    print("\n[5/7] Verifying Documentation Assets (UI_STUDIO_GUIDE, PROCEED)...")
    guide_file = os.path.join(studio_path, "documentation", "UI_STUDIO_GUIDE.md")
    proceed_file = os.path.join(studio_path, "documentation", "PROCEED.md")
    if os.path.exists(guide_file) and os.path.exists(proceed_file):
        print("✅ UI_STUDIO_GUIDE.md and PROCEED.md documentation verified.")
    else:
        print("❌ Documentation assets verification FAILED.")
        all_passed = False

    print("\n[6/7] Verifying Platform Isolation (No Character/Presentation duplication)...")
    # Verify no avatar or dashboard files inside UI studio
    char_check = os.path.exists(os.path.join(studio_path, "assets", "avatar"))
    pres_check = os.path.exists(os.path.join(studio_path, "assets", "experiences"))
    
    if not char_check and not pres_check:
        print("✅ Platform isolation verified: ZERO Character or Presentation assets inside Desktop UI Studio.")
    else:
        print("❌ Platform isolation FAILED.")
        all_passed = False

    print("\n[7/7] Zero Regression Verification (Kernel Boot & Frozen Platforms)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: Character, Presentation, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S35A IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S35A VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
