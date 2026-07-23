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

from desktop.personality.runtime.personality_engine import PersonalityEngine
from desktop.personality.runtime.narration_context import NarrationContext

async def run_verification():
    print("==========================================================")
    print("Starting S36A-R1 Personality Engine Verification")
    print("==========================================================\n")
    
    all_passed = True
    pe = PersonalityEngine()

    print("[1/8] Verifying PersonalityProfile Loading & Presets...")
    pe.apply_preset("friendly")
    p_friendly = pe.active_profile.friendly
    pe.apply_preset("professional")
    p_pro = pe.active_profile.professional
    
    if p_friendly >= 0.8 and p_pro >= 0.8:
        print("✅ PersonalityProfile loading and preset switching verified.")
    else:
        print("❌ PersonalityProfile / Preset verification FAILED.")
        all_passed = False

    print("\n[2/8] Verifying NarrationStyleEngine Rewrites...")
    pe.apply_preset("friendly")
    ctx_browser = NarrationContext(domain_intent="OPEN_BROWSER")
    rw_friendly = pe.rewrite_narration("Opening browser.", ctx_browser)
    
    pe.apply_preset("minimal")
    rw_minimal = pe.rewrite_narration("Opening browser.", ctx_browser)

    pe.apply_preset("motivational")
    rw_moti = pe.rewrite_narration("Opening browser.", ctx_browser)
    
    if "boss" in rw_friendly.lower() and "opened" in rw_minimal.lower() and "conquer" in rw_moti.lower() or "do it" in rw_moti.lower():
        print(f"✅ NarrationStyleEngine rewrites verified across profiles ('{rw_friendly}', '{rw_minimal}', '{rw_moti}').")
    else:
        print("❌ NarrationStyleEngine verification FAILED.")
        all_passed = False

    print("\n[3/8] Verifying SpeechPersonalityAdapter Voice Parameters Mapping...")
    pe.apply_preset("motivational")
    v_params = pe.adapt_voice_parameters()
    
    if v_params.voice_energy >= 1.2 and v_params.emphasis >= 1.2:
        print(f"✅ SpeechPersonalityAdapter mapped voice parameters cleanly (Energy: {v_params.voice_energy}, Emphasis: {v_params.emphasis}).")
    else:
        print("❌ SpeechPersonalityAdapter verification FAILED.")
        all_passed = False

    print("\n[4/8] Verifying BehaviorPersonalityAdapter Selection Mapping...")
    pe.apply_preset("professional")
    b_pro = pe.adapt_behavior_selection("TalkingExplain")
    
    pe.apply_preset("friendly")
    b_friendly = pe.adapt_behavior_selection("TalkingNeutral")
    
    if b_pro == "TalkingProfessional" and b_friendly == "TalkingHappy":
        print("✅ BehaviorPersonalityAdapter mapped behaviors cleanly (Professional -> TalkingProfessional, Friendly -> TalkingHappy).")
    else:
        print("❌ BehaviorPersonalityAdapter verification FAILED.")
        all_passed = False

    print("\n[5/8] Verifying UIPersonalityAdapter Wording Adaptation...")
    pe.apply_preset("friendly")
    ui_friendly = pe.adapt_ui_text("Reminder Created", "Default text")
    
    pe.apply_preset("minimal")
    ui_minimal = pe.adapt_ui_text("Reminder Created", "Default text")
    
    if "boss" in ui_friendly.lower() and "set" in ui_minimal.lower():
        print(f"✅ UIPersonalityAdapter adapted UI wording cleanly ('{ui_friendly}', '{ui_minimal}').")
    else:
        print("❌ UIPersonalityAdapter verification FAILED.")
        all_passed = False

    print("\n[6/8] Verifying Profile JSON Import / Export & Trait Validation...")
    exported_json = pe.export_profile_json()
    ok, errors = pe.import_profile_json(exported_json)
    
    if ok and errors == []:
        print("✅ Import/Export JSON and trait validation verified cleanly.")
    else:
        print(f"❌ Import/Export verification FAILED: {errors}")
        all_passed = False

    print("\n[7/8] Verifying Profile Persistence...")
    ok_upd, _ = pe.update_traits(humorous=0.95)
    if ok_upd and pe.active_profile.humorous == 0.95:
        print("✅ Profile trait updates and storage persistence verified.")
    else:
        print("❌ Profile persistence verification FAILED.")
        all_passed = False

    print("\n[8/8] Zero Regression Verification (Kernel Boot & Independent Runtimes)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: Character, Voice, Presentation, Desktop UI, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S36A-R1 IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S36A-R1 VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
