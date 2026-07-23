import sys
import os
import time
import threading

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, v3_root)

from desktop.platform.integrations.core.event_bus import EventBus
from desktop.services.audio.providers.piper_provider import PiperProvider
from desktop.platform.integrations.core.provider_registry import SpeechSynthRegistry
from desktop.services.audio.speech_synth_router import SpeechSynthRouter
from desktop.runtimes.expression.outputs.voice.runtime import VoiceRuntime
from desktop.runtimes.expression.outputs.voice.events import SpeakRequested
from desktop.platform.shared.interfaces.event_bus import Event

class MockLogger:
    def info(self, msg): pass
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): pass
    def debug(self, msg): pass
    def event(self, event_id, **kwargs): pass
    def exception(self, e, **kwargs): print(f"EXC: {e}")

def main():
    print("Starting Rapid Interruption Stress Test...")
    
    mlogger = MockLogger()
    event_bus = EventBus(logger=mlogger)
    event_bus.start()
    
    piper = PiperProvider(event_bus=event_bus, logger=mlogger)
    model_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper\en_US-lessac-medium.onnx"
    piper.load_model(model_path)
    
    registry = SpeechSynthRegistry(logger=mlogger)
    registry.register_provider(piper)
    router = SpeechSynthRouter(registry=registry, logger=mlogger)
    
    voice_runtime = VoiceRuntime(event_bus=event_bus, speech_router=router)
    voice_runtime.start()

    print("\n--- Test 1: Overlapping Requests ---")
    print("Sending 'Hello'...")
    event_bus.publish(SpeakRequested(text="Hello"))
    time.sleep(0.1) # Immediately follow up
    print("Sending 'How are you?'...")
    event_bus.publish(SpeakRequested(text="How are you?"))
    
    time.sleep(3) # Let it play out

    print("\n--- Test 2: Rapid Interruption (50 times) ---")
    
    for i in range(50):
        if i % 10 == 0:
            print(f"Iteration {i}/50...")
            
        event_bus.publish(SpeakRequested(text="The weather today is very nice and sunny."))
        time.sleep(0.1) # Let it barely start synthesizing/playing
        
        # Simulate Wake Word interrupt
        event_bus.publish(Event("WakeDetected", "Mic", {}))
        time.sleep(0.05) # Brief pause before next
        
    print("\nStress testing complete. Verify no crash or memory explosion.")
    
    # Check active threads
    active_threads = threading.enumerate()
    print(f"\nActive threads ({len(active_threads)}):")
    for t in active_threads:
        print(f" - {t.name}")

if __name__ == "__main__":
    main()
