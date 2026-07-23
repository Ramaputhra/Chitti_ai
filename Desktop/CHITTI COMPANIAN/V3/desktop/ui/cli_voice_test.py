import sys
import os
import time

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, v3_root)

from desktop.platform.integrations.core.event_bus import EventBus
from desktop.services.audio.providers.piper_provider import PiperProvider
from desktop.services.audio.providers.faster_whisper_provider import FasterWhisperProvider
from desktop.platform.integrations.core.provider_registry import SpeechSynthRegistry
from desktop.services.audio.speech_synth_router import SpeechSynthRouter
from desktop.runtimes.expression.outputs.voice.runtime import VoiceRuntime
from desktop.runtimes.expression.outputs.voice.events import SpeakRequested
from desktop.runtimes.audio.input.runtime import AudioInputRuntime
from desktop.platform.ai.speech_orchestrator import SpeechOrchestrator

class CLILogger:
    def info(self, msg): print(f"[INFO] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")
    def warning(self, msg): print(f"[WARN] {msg}")
    def debug(self, msg): pass
    def event(self, event_id, **kwargs): pass
    def exception(self, e, **kwargs): print(f"[EXC] {e}")

class MockLLM:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("USER_TRANSCRIPT_GENERATED", self._on_transcript)
            
    def _on_transcript(self, event_data):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict):
            payload = event_data.get("payload", {})
            
        text = payload.get("text", "")
        print(f"\n[MockLLM] Received transcript: '{text}'")
        
        if not text.strip():
            print("[MockLLM] Transcript empty, ignoring.")
            return
        
        response = f"I heard you say: {text}"
        print(f"[MockLLM] Replying with: '{response}'")
        
        import threading
        def reply():
            time.sleep(0.5)
            if hasattr(self.event_bus, "publish"):
                self.event_bus.publish(SpeakRequested(text=response))
                
        threading.Thread(target=reply, daemon=True).start()

class CLIEventPrinter:
    def __init__(self, event_bus):
        event_bus.subscribe("WAKE_WORD_DETECTED", lambda e: print("\n>>> EVENT: WAKE WORD DETECTED! <<<"))
        event_bus.subscribe("SPEECH_STARTED", lambda e: print(">>> EVENT: SPEECH STARTED... <<<"))
        event_bus.subscribe("SPEECH_STOPPED", lambda e: print(">>> EVENT: SPEECH STOPPED! <<<"))
        event_bus.subscribe("SPEECH_STATE_CHANGED", lambda e: print(f">>> EVENT: STATE -> {getattr(e, 'payload', e.get('payload', {}) if isinstance(e, dict) else {}).get('state')} <<<"))
        event_bus.subscribe("TRANSCRIBE_BUFFER", lambda e: print(">>> EVENT: TRANSCRIBING AUDIO BUFFER... <<<"))
        event_bus.subscribe("Voice.AudioStarted", lambda e: print(">>> EVENT: TTS AUDIO PLAYING... <<<"))
        event_bus.subscribe("Voice.AudioFinished", lambda e: print(">>> EVENT: TTS AUDIO FINISHED <<<"))

def main():
    print("=== CHITTI CLI PIPELINE TEST ===")
    
    logger = CLILogger()
    event_bus = EventBus(logger=logger)
    event_bus.start()
    
    printer = CLIEventPrinter(event_bus)
    
    print("\n[1/4] Loading Piper TTS...")
    piper = PiperProvider(event_bus=event_bus, logger=logger)
    piper.load_model(r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper\en_US-amy-medium.onnx")
    registry = SpeechSynthRegistry(logger=logger)
    registry.register_provider(piper)
    router = SpeechSynthRouter(registry=registry, logger=logger)
    voice_runtime = VoiceRuntime(event_bus=event_bus, speech_router=router)
    voice_runtime.start()
    
    print("\n[2/4] Loading FasterWhisper STT (Small Multi-lingual)...")
    whisper = FasterWhisperProvider(event_bus=event_bus, logger=logger)
    whisper.load_model("small")
    
    print("\n[3/4] Starting OpenWakeWord & Microphone...")
    audio_input = AudioInputRuntime(event_bus=event_bus)
    audio_input.start()
    
    print("\n[4/4] Starting Orchestrator & Mock LLM...")
    orchestrator = SpeechOrchestrator(event_bus=event_bus)
    mock_llm = MockLLM(event_bus)
    
    print("\n==============================================")
    print("ALL SYSTEMS GO! Say 'Alexa' to wake CHITTI up.")
    print("Press Ctrl+C to exit.")
    print("==============================================\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        audio_input.stop()
        voice_runtime.stop()

if __name__ == "__main__":
    main()
