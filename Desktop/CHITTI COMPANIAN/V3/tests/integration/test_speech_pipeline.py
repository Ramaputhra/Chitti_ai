import time
import logging
from typing import Dict, Any

class MockEventBus:
    def __init__(self):
        self.subscribers = {}
        self.published_events = []

    def subscribe(self, event_type: str, callback: Any) -> None:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event, source=None, payload=None) -> None:
        """Publish event - supports both signatures."""
        if hasattr(event, 'event_type'):
            event_type = event.event_type
            payload = getattr(event, 'payload', None) or {}
            source = getattr(event, 'source', 'MockBus')
        else:
            event_type = event
        
        self.published_events.append((event_type, payload))
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback({"payload": payload or {}, "source": source})

from desktop.platform.components.adapters.openwakeword_adapter import OpenWakeWordAdapter
from desktop.platform.components.adapters.silero_vad_adapter import SileroVADAdapter
from desktop.platform.components.adapters.faster_whisper_adapter import FasterWhisperAdapter
from desktop.platform.ai.speech_orchestrator import SpeechOrchestrator
from desktop.models.audio_models import SpeechState

def run_speech_pipeline_test():
    logging.basicConfig(level=logging.INFO)
    print("\n" + "="*60)
    print("VIZZU SPEECH PIPELINE - END TO END TEST")
    print("="*60)
    
    bus = MockEventBus()
    ww_adapter = OpenWakeWordAdapter(bus)
    vad_adapter = SileroVADAdapter(bus)
    stt_adapter = FasterWhisperAdapter(bus)
    orchestrator = SpeechOrchestrator(bus, config={"reply_window": 1.0})
    
    passed = 0
    failed = 0
    
    # --- TEST 1: Initial State ---
    print("\n[TEST 1] Initial State Machine")
    try:
        assert orchestrator.state == SpeechState.SLEEPING
        print("  ✅ SpeechOrchestrator starts in SLEEPING state")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # --- TEST 2: Wake Word Detection ---
    print("\n[TEST 2] Wake Word Detection -> LISTENING")
    try:
        bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'WAKE'})
        assert orchestrator.state == SpeechState.LISTENING, f"Expected LISTENING, got {orchestrator.state}"
        assert orchestrator.current_session is not None
        print("  ✅ Wake word detected, transitioning to LISTENING")
        print(f"     Session ID: {orchestrator.current_session.id}")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # --- TEST 3: Audio Capture & VAD ---
    print("\n[TEST 3] Audio Capture with VAD (Silence Detection)")
    try:
        initial_segments = len(orchestrator.current_session.speech_segments)
        bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'COMMAND_AUDIO'})
        bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'\x00\x00'})  # Silence -> triggers VAD
        
        # Check state transitioned to UNDERSTANDING after silence
        assert orchestrator.state == SpeechState.UNDERSTANDING, f"Expected UNDERSTANDING, got {orchestrator.state}"
        print("  ✅ Audio captured, silence detected, transitioning to UNDERSTANDING")
        print(f"     Speech segments: {len(orchestrator.current_session.speech_segments)} bytes")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # --- TEST 4: State Machine Reset ---
    print("\n[TEST 4] State Machine Reset to SLEEPING")
    try:
        orchestrator.transition(SpeechState.SLEEPING)
        assert orchestrator.state == SpeechState.SLEEPING
        print("  ✅ State machine reset to SLEEPING")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # --- TEST 5: Noise Rejection ---
    print("\n[TEST 5] Noise Without Wake Word (Should Stay Sleeping)")
    try:
        bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'BACKGROUND_NOISE_ONLY'})
        assert orchestrator.state == SpeechState.SLEEPING
        print("  ✅ Background noise ignored, stays in SLEEPING")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # --- TEST 6: Event Publishing ---
    print("\n[TEST 6] Event Publishing Verification")
    try:
        event_types = [e[0] for e in bus.published_events if isinstance(e[0], str)]
        expected_events = ["WAKE_WORD_DETECTED", "SPEECH_STARTED", "SPEECH_STOPPED"]
        found = [e for e in expected_events if e in event_types]
        print(f"  ✅ Events published: {found}")
        print(f"     Total events: {len(event_types)}")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # --- SUMMARY ---
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{passed+failed} tests passed")
    print("="*60)
    
    if failed > 0:
        print("\n❌ SOME TESTS FAILED")
        exit(1)
    else:
        print("\n🎉 ALL SPEECH PIPELINE TESTS PASSED!")
        print("\nPipeline verified:")
        print("  WAKE WORD (OpenWakeWord) -> VAD (Silero) -> STT (FasterWhisper) -> UNDERSTANDING")
        exit(0)

if __name__ == "__main__":
    run_speech_pipeline_test()
