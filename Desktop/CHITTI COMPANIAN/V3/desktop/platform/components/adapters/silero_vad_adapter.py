import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class SileroVADAdapter:
    """
    Adapter for the Silero Voice Activity Detection model.
    Subscribes to AUDIO_CHUNK_CAPTURED and emits SPEECH_STARTED / SPEECH_STOPPED.
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self.event_bus.subscribe("AUDIO_CHUNK_CAPTURED", self.process_chunk)
        self.is_speaking = False
        self.speech_buffer = bytearray()
        
    def process_chunk(self, event: Dict[str, Any]) -> None:
        chunk = event.get("payload", {}).get("data", b"")
        
        # Mock VAD logic
        has_speech = self._detect_speech_mock(chunk)
        
        if has_speech and not self.is_speaking:
            self.is_speaking = True
            self.speech_buffer = bytearray(chunk)
            self.event_bus.publish("SPEECH_STARTED", source="SileroVADAdapter", payload={})
            
        elif has_speech and self.is_speaking:
            self.speech_buffer.extend(chunk)
            
        elif not has_speech and self.is_speaking:
            self.is_speaking = False
            self.event_bus.publish("SPEECH_STOPPED", source="SileroVADAdapter", payload={"buffer": bytes(self.speech_buffer)})
            self.speech_buffer = bytearray()
            
    def _detect_speech_mock(self, chunk: bytes) -> bool:
        # Returns False for absolute silence, True if there's noise
        return any(b != 0 for b in chunk)
