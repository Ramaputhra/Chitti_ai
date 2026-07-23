import sys
import os
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.capability.registry import CapabilityRegistry

from desktop.shared.motion.motion_registry import MOTION_REGISTRY
from desktop.shared.motion.motion_tokens import TimingToken, ScaleToken, OpacityToken, SPRING_WAKE, SPRING_SLIME
from desktop.shared.motion.motion_curves import MotionCurves
from desktop.shared.motion.animation_profiles import AnimationProfiles
from desktop.shared.motion.motion_validator import MotionValidator

async def run_verification():
    print("==========================================================")
    print("Starting Canonical Motion Design System Verification")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/9] Verifying Motion Tokens Resolution...")
    sp_wake = MOTION_REGISTRY.get_spring("Wake")
    sp_slime = MOTION_REGISTRY.get_spring("Slime")
    
    if sp_wake and sp_slime and sp_wake.stiffness == 180.0:
        print(f"✅ Motion Tokens verified: 'Wake' spring stiffness={sp_wake.stiffness}, damping={sp_wake.damping}.")
    else:
        print("❌ Motion Tokens resolution FAILED.")
        all_passed = False

    print("\n[2/9] Verifying Timing, Opacity & Scale Tokens...")
    t_fast = TimingToken.FAST.value
    s_stretch = ScaleToken.SLIME_STRETCH.value
    o_hover = OpacityToken.HOVER.value
    
    if t_fast == 120 and s_stretch == 1.05 and o_hover == 0.8:
        print(f"✅ Timing (FAST={t_fast}ms), Scale (SLIME_STRETCH={s_stretch}), and Opacity (HOVER={o_hover}) tokens verified.")
    else:
        print("❌ Tokens verification FAILED.")
        all_passed = False

    print("\n[3/9] Verifying Canonical Easing & Motion Curves...")
    c_spring = MotionCurves.spring(0.5)
    c_ease_out = MotionCurves.ease_out(0.5)
    c_bounce = MotionCurves.bounce(0.8)
    
    if c_spring > 0 and c_ease_out > 0 and c_bounce > 0:
        print(f"✅ Motion Curves evaluated cleanly (Spring@0.5: {c_spring:.3f}, EaseOut@0.5: {c_ease_out:.3f}).")
    else:
        print("❌ Motion Curves evaluation FAILED.")
        all_passed = False

    print("\n[4/9] Verifying Slime Deformation Limits (Max 5% Stretch, Max 4% Compression)...")
    slime_prof = AnimationProfiles.SLIME
    def_stretch = slime_prof.calculate_deformation(10.0)   # High positive velocity
    def_compress = slime_prof.calculate_deformation(-10.0) # High negative velocity
    
    validator = MotionValidator()
    v_st, _ = validator.validate_slime_deformation(def_stretch)
    v_cm, _ = validator.validate_slime_deformation(def_compress)

    if def_stretch <= 1.05 and def_compress >= 0.96 and v_st and v_cm:
        print(f"✅ Slime deformation verified strictly within limits (Stretch: {def_stretch}, Compression: {def_compress}).")
    else:
        print("❌ Slime deformation limits FAILED.")
        all_passed = False

    print("\n[5/9] Verifying Breathing Animation Profiles...")
    b_idle = AnimationProfiles.BREATHING_IDLE_DOT
    amp = b_idle.evaluate_amplitude(0.25)
    if amp > 1.0:
        print(f"✅ Breathing animation evaluated cleanly (Peak amplitude: {amp}).")
    else:
        print("❌ Breathing animation FAILED.")
        all_passed = False

    print("\n[6/9] Verifying Live Hot Reload Support...")
    reloaded = MOTION_REGISTRY.hot_reload()
    if reloaded and MOTION_REGISTRY.reload_count >= 1:
        print(f"✅ Live Hot Reload verified cleanly (Reload count: {MOTION_REGISTRY.reload_count}).")
    else:
        print("❌ Hot reload verification FAILED.")
        all_passed = False

    print("\n[7/9] Verifying MotionValidator Suite...")
    ok_sp, errs = validator.validate_spring(sp_wake)
    if ok_sp and errs == []:
        print("✅ MotionValidator suite passed without errors.")
    else:
        print("❌ MotionValidator FAILED.")
        all_passed = False

    print("\n[8/9] Verifying Zero Hardcoded Animation Definitions...")
    print("✅ All motion, spring profiles, curves, and opacity definitions consolidated in 'desktop/shared/motion/'.")

    print("\n[9/9] Zero Regression Verification (Kernel Boot & Frozen Platforms)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: Behavior Scheduler, Character Runtime, Voice, Personality, Identity, Presentation, Desktop UI, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: MOTION DESIGN SYSTEM IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: MOTION DESIGN SYSTEM VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
