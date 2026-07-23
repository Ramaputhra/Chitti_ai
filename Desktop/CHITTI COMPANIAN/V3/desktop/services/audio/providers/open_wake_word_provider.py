import time
from typing import Any, Dict

import numpy as np

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.wake_word import IWakeWordProvider
from desktop.platform.shared.models.audio import AudioPacket

try:
    import openwakeword
    from openwakeword.model import Model
except ImportError:
    openwakeword = None
    Model = None


class OpenWakeWordProvider(IWakeWordProvider):
    """
    Uses openwakeword to detect wake words locally.
    Listens to VOICE_AUDIO_FRAME events from the MicrophoneManager.
    """
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._model = None
        self._is_listening = False
        self._target_wake_word = "hey_chitti"  # Assuming we use a custom or default
        
        # Openwakeword defaults
        self._threshold = 0.2

    @property
    def name(self) -> str:
        return "OpenWakeWordProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        if Model is None:
            self.logger.error("openwakeword is not installed. Run: pip install openwakeword")
            self._state = ServiceState.ERROR
            return
            
        try:
            # For demonstration, we use a pre-trained model like "hey_jarvis" or similar if hey_chitti isn't trained.
            # In production, we'd load a custom model.
            openwakeword.utils.download_models() # ensures default models are present
            # We'll use a default model to avoid crash if custom doesn't exist
            self._model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
            self.logger.info(f"{self.name} initialized with model")
            
            self.event_bus.subscribe(SystemEvents.VOICE_AUDIO_FRAME, self._on_audio_frame)
            self._state = ServiceState.RUNNING
        except Exception as e:
            self.logger.exception(e, module=self.name)
            self._state = ServiceState.ERROR

    def shutdown(self) -> None:
        self._is_listening = False
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {
            "model_loaded": self._model is not None,
            "is_listening": self._is_listening
        }

    def start_listening(self) -> None:
        if self._state == ServiceState.RUNNING:
            self._is_listening = True
            self.logger.info("Wake word listening started")

    def stop_listening(self) -> None:
        self._is_listening = False
        self.logger.info("Wake word listening stopped")

    def trigger_wake(self) -> None:
        # Manual trigger (used for testing or explicit button press)
        self.logger.info("Wake Word manually triggered!")
        self._is_listening = False # Usually we stop listening for wake word while handling the intent
        self.event_bus.publish(
            Event("Voice.WakeDetected", self.name, {"wake_word": "manual"})
        )

    def _on_audio_frame(self, event: Event) -> None:
        if not self._is_listening or self._state != ServiceState.RUNNING or not self._model:
            return

        packet: AudioPacket = event.payload.get("packet")
        if not packet:
            return

        # openwakeword expects 16kHz 16-bit PCM audio
        audio_data = np.frombuffer(packet.data, dtype=np.int16)
        
        # Predict
        prediction = self._model.predict(audio_data)
        
        # Check if any wake word crossed the threshold
        for ww, score in prediction.items():
            if score > 0.05:  # Log low scores for debugging
                self.logger.info(f"[DEBUG] Wake Word '{ww}' score: {score:.3f}")
                
            if score > self._threshold:
                self.logger.info(f"Wake Word detected: {ww} (score: {score:.3f})")
                self.event_bus.publish(
                    Event("Voice.WakeDetected", self.name, {"wake_word": ww, "score": score})
                )
                self.stop_listening() # Stop listening until reactivated by the pipeline
                break
