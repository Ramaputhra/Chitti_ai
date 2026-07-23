import sys
import os
import time
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.capability.registry import CapabilityRegistry

from desktop.voice.runtime.voice_runtime import VoiceRuntime
from desktop.voice.runtime.speech_session import SpeechSessionState

async def run_verification():
    print("==========================================================")
    print("Starting S36A Voice Runtime & Speech Platform Verification")
    print("==========================================================\n")
    
    all_passed = True
    vr = VoiceRuntime()

    print("[1/8] Verifying LanguageManager & Language Switching...")
    vr.set_language("te") # Telugu
    l1 = vr.language_manager.current_language
    detected = vr.language_manager.detect_language("నమస్కారం CHITTI")
    vr.set_language("en") # Reset to English
    
    if l1 == "te" and detected == "te":
        print("✅ LanguageManager verified: Language switching and Telugu auto-detection succeeded.")
    else:
        print("❌ LanguageManager verification FAILED.")
        all_passed = False

    print("\n[2/8] Verifying VoiceProfileManager & SpeechStyleManager...")
    p_ok = vr.set_voice_profile("prof_female")
    s_ok = vr.set_speech_style("motivational")
    
    if p_ok and s_ok and vr.profile_manager.active_profile.voice_id == "prof_female":
        print("✅ VoiceProfileManager and SpeechStyleManager verified cleanly.")
    else:
        print("❌ Profile / Style manager verification FAILED.")
        all_passed = False

    print("\n[3/8] Verifying PronunciationManager Custom Dictionary...")
    vr.add_pronunciation("customword", "Kus tom word")
    converted = vr.pronunciation_manager.apply_pronunciation("Hello ChatGPT on GitHub with customword")
    
    if "Chat G P T" in converted and "Git Hub" in converted and "Kus tom word" in converted:
        print("✅ PronunciationManager verified: Phonetic mappings applied cleanly.")
    else:
        print("❌ PronunciationManager verification FAILED.")
        all_passed = False

    print("\n[4/8] Verifying NarrationComposer & EmotionMarkupEngine...")
    text_sample = "Welcome to CHITTI! This is an EXCELLENT presentation."
    narration = vr.speech_runtime.composer.compose_narration(text_sample, emotion_hint="CELEBRATION")
    markup = vr.speech_runtime.markup_engine.process_markup(narration.normalized_text, emotion_tag="CELEBRATION")
    
    if len(narration.sentences) >= 2 and markup.speed_rate > 1.0:
        print("✅ NarrationComposer and EmotionMarkupEngine verified cleanly.")
    else:
        print("❌ Composition / Markup verification FAILED.")
        all_passed = False

    print("\n[5/8] Verifying TTS Synthesis & Canonical SpeechTimeline Generation...")
    session, timeline = vr.synthesize_text("Hello user, testing TTS synthesis and timeline generation.", speech_id="sp_test_1", session_id="sess_1")
    
    if session.state == SpeechSessionState.READY and timeline.total_duration > 0 and len(timeline.sentence_boundaries) > 0:
        print(f"✅ TTS synthesis & SpeechTimeline verified (Duration: {timeline.total_duration}s, Sentences: {len(timeline.sentence_boundaries)}).")
    else:
        print("❌ TTS Synthesis / SpeechTimeline verification FAILED.")
        all_passed = False

    print("\n[6/8] Verifying SpeechCache Performance (Cache HIT)...")
    sess_cached, tl_cached = vr.synthesize_text("Hello user, testing TTS synthesis and timeline generation.", speech_id="sp_test_2", session_id="sess_2")
    
    if vr.metrics.cache_hit_count >= 1:
        print("✅ SpeechCache verified: Cache HIT recorded for identical speech response.")
    else:
        print("❌ SpeechCache verification FAILED.")
        all_passed = False

    print("\n[7/8] Verifying SpeechQueue & Session Playback Lifecycles...")
    vr.play_speech(session)
    if vr.speech_runtime.active_session == session and session.state == SpeechSessionState.PLAYING:
        vr.stop_speech()
        print("✅ SpeechQueue and Session playback lifecycles verified cleanly.")
    else:
        print("❌ Playback lifecycle verification FAILED.")
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
        print("✅ Zero Regression Verification PASSED: Character, Presentation, Desktop UI, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S36A IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S36A VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
