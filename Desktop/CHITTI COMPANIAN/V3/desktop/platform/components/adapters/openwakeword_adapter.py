import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class OpenWakeWordAdapter:
    """
    Adapter for the openWakeWord model.
    Constantly evaluates audio, but safely ignores triggers when the orchestrator is active.
    """
    def __init__(self, event_bus: Any, model_path: str = "desktop/models/audio/chitti.onnx"):
        self.event_bus = event_bus
        self.model_path = model_path
        self.ignore_triggers = False
        
        self.event_bus.subscribe("AUDIO_CHUNK_CAPTURED", self.process_chunk)
        self.event_bus.subscribe("SPEECH_STATE_CHANGED", self.on_state_changed)
        logger.debug(f"OpenWakeWordAdapter initialized with model: {model_path}")

    def on_state_changed(self, event: Dict[str, Any]) -> None:
        state = event.get("payload", {}).get("state", "SLEEPING")
        self.ignore_triggers = (state != "SLEEPING")

    def process_chunk(self, event: Dict[str, Any]) -> None:
        if self.ignore_triggers:
            return
            
        chunk = event.get("payload", {}).get("data", b"")
        detected = self._detect_wakeword_mock(chunk)
        
        if detected:
            logger.info("Wake word detected!")
            self.event_bus.publish("WAKE_WORD_DETECTED", source="OpenWakeWordAdapter", payload={"model": self.model_path})

    def _detect_wakeword_mock(self, chunk: bytes) -> bool:
        return b'WAKE' in chunk
