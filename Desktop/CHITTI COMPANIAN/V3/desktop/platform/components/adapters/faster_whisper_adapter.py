import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class FasterWhisperAdapter:
    """
    Adapter for the Faster-Whisper Speech-to-Text model.
    Subscribes to TRANSCRIBE_BUFFER (sent by the Orchestrator after VAD stops).
    Emits USER_TRANSCRIPT_GENERATED with language metadata.
    """
    def __init__(self, event_bus: Any, model_size: str = "base"):
        self.event_bus = event_bus
        self.model_size = model_size
        self.event_bus.subscribe("TRANSCRIBE_BUFFER", self.transcribe)
        logger.debug(f"FasterWhisperAdapter initialized with size: {model_size}")

    def transcribe(self, event: Dict[str, Any]) -> None:
        payload = event.get("payload", {})
        buffer = payload.get("buffer", b"")
        session_id = payload.get("session_id")
        
        if not buffer:
            return
            
        logger.info(f"Transcribing {len(buffer)} bytes of audio for session {session_id}...")
        
        # Mock Transcription returning (text, language)
        transcript, lang = self._transcribe_mock(buffer)
        
        if transcript:
            logger.info(f"Transcription complete: [{lang}] '{transcript}'")
            self.event_bus.publish("USER_TRANSCRIPT_GENERATED", source="FasterWhisperAdapter", payload={
                "session_id": session_id,
                "text": transcript,
                "language": lang
            })
            
    def _transcribe_mock(self, buffer: bytes) -> (str, str):
        if b'MOCK_DOWNLOADS' in buffer:
            return "Open Downloads", "en"
        if b'MOCK_SCREENPLAY' in buffer:
            return "Open my screenplay", "en"
        return "Unknown command", "en"
