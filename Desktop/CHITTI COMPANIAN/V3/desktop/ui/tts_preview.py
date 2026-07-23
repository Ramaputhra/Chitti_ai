import sys
import os
import time
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from desktop.platform.integrations.core.event_bus import EventBus
from desktop.services.audio.providers.piper_provider import PiperProvider
from desktop.platform.integrations.core.provider_registry import SpeechSynthRegistry
from desktop.services.audio.speech_synth_router import SpeechSynthRouter
from desktop.runtimes.expression.outputs.voice.runtime import VoiceRuntime
from desktop.runtimes.expression.outputs.voice.events import SpeakRequested

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TTSPreview")

# Mock Logger
class MockLogger:
    def info(self, msg): logger.info(msg)
    def error(self, msg): logger.error(msg)
    def warning(self, msg): logger.warning(msg)
    def debug(self, msg): logger.debug(msg)
    def event(self, event_id, **kwargs): logger.info(f"EVENT: {event_id} {kwargs}")
    def exception(self, e, **kwargs): logger.error(f"EXCEPTION: {e} {kwargs}")

def main():
    print("=== CHITTI TTS PREVIEW ===")
    
    model_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper\en_US-amy-medium.onnx"
    if not os.path.exists(model_path):
        print(f"\n[ERROR] Piper model not found at {model_path}")
        print("Please run `python scripts/download_piper_model.py` first.\n")
        return

    # 1. Setup Infrastructure
    mlogger = MockLogger()
    event_bus = EventBus(logger=mlogger)
    event_bus.start()
    
    # 2. Setup Piper Provider
    piper = PiperProvider(event_bus=event_bus, logger=mlogger)
    if not piper.load_model(model_path):
        print("\n[ERROR] Failed to load piper model. Make sure piper-tts is installed.")
        return
        
    registry = SpeechSynthRegistry(logger=mlogger)
    registry.register_provider(piper)
    
    # 3. Setup Router
    router = SpeechSynthRouter(registry=registry, logger=mlogger)
    
    # 4. Setup Voice Runtime
    voice_runtime = VoiceRuntime(event_bus=event_bus, speech_router=router)
    voice_runtime.start()
    
    print("\n[System] TTS Engine Online. Type text and press Enter to hear it.")
    print("[System] Type 'quit' to exit. Type 'stop' to instantly interrupt audio.")
    
    while True:
        try:
            text = input("\n> ")
            if text.strip().lower() == "quit":
                break
            elif text.strip().lower() == "stop":
                voice_runtime._stop_playback("user_interrupt")
                continue
                
            if text.strip():
                # Emitting SpeakRequested will trigger VoiceRuntime
                event_bus.publish(SpeakRequested(text=text))
                
        except KeyboardInterrupt:
            break
            
    voice_runtime.stop()
    print("Exiting...")

if __name__ == "__main__":
    main()
