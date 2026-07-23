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

    def publish(self, event_type: str, source: str, payload: Dict[str, Any] = None) -> None:
        self.published_events.append((event_type, payload))
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback({"payload": payload or {}})

from desktop.platform.components.adapters.openwakeword_adapter import OpenWakeWordAdapter
from desktop.platform.components.adapters.silero_vad_adapter import SileroVADAdapter
from desktop.platform.components.adapters.faster_whisper_adapter import FasterWhisperAdapter
from desktop.platform.ai.speech_orchestrator import SpeechOrchestrator
from desktop.models.audio_models import SpeechState

def run_speech_pipeline_test():
    logging.basicConfig(level=logging.INFO)
    print("\n--- Running Refactored Speech Pipeline Test ---")
    
    bus = MockEventBus()
    ww_adapter = OpenWakeWordAdapter(bus)
    vad_adapter = SileroVADAdapter(bus)
    stt_adapter = FasterWhisperAdapter(bus)
    orchestrator = SpeechOrchestrator(bus, config={"reply_window": 1.0})
    
    # --- TEST 1: The Golden Path ---
    assert orchestrator.state == SpeechState.SLEEPING
    print("\n[TEST 1: Golden Path - User says 'Open Downloads']")
    bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'WAKE'})
    
    assert orchestrator.state == SpeechState.LISTENING
    assert orchestrator.current_session is not None
    session_id = orchestrator.current_session.id
    
    bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'MOCK_DOWNLOADS_CHUNK_1'})
    bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'\x00\x00'}) # Silence
    
    assert orchestrator.state == SpeechState.TRANSCRIBING
    transcripts = [e for e in bus.published_events if e[0] == "USER_TRANSCRIPT_GENERATED"]
    assert len(transcripts) == 1
    assert orchestrator.current_session.transcript == "Open Downloads"
    assert orchestrator.current_session.language == "en"
    print("✅ Success! Transcript and Language generated and attached to session.")

    # --- TEST 2: Echo Protection ---
    print("\n[TEST 2: Echo Protection]")
    bus.publish("TTS_STARTED", "Piper", {})
    # While TTS is playing, someone speaks. It should be ignored.
    bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'WAKE'})
    bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'MOCK_DOWNLOADS_CHUNK_3'})
    bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'\x00\x00'})
    
    # We should not have generated a second transcript
    transcripts_now = [e for e in bus.published_events if e[0] == "USER_TRANSCRIPT_GENERATED"]
    assert len(transcripts_now) == 1 # Still 1
    print("✅ Success! TTS audio was ignored by STT and Wake Word.")
    
    bus.publish("TTS_FINISHED", "Piper", {})
    assert orchestrator.state == SpeechState.EXPECTING_REPLY

    # --- TEST 3: Noise Protection ---
    print("\n[TEST 3: Noise Without Wake Word]")
    orchestrator.transition(SpeechState.SLEEPING)
    # Just random noise (not the wake word)
    bus.publish("AUDIO_CHUNK_CAPTURED", "Mic", {"data": b'LOUD_TV_NOISE'})
    assert orchestrator.state == SpeechState.SLEEPING
    print("✅ Success! Background noise ignored without wake word.")

if __name__ == "__main__":
    run_speech_pipeline_test()
