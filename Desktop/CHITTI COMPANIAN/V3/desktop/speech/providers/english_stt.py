import asyncio
from typing import List, Optional
from desktop.speech.providers.base import ISTTProvider
from desktop.speech.models import SpeechTranscribed

class EnglishSTTProvider(ISTTProvider):
    """Wraps faster-whisper for primary English transcription."""
    
    def __init__(self):
        # In a real implementation: self.model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        self._is_loaded = False
        
    def load(self):
        self._is_loaded = True
        
    def get_supported_languages(self) -> List[str]:
        return ["en"]
        
    async def transcribe_stream(self, audio_chunk: bytes) -> Optional[SpeechTranscribed]:
        if not self._is_loaded:
            return None
            
        # Mocking faster-whisper transcribe for Phase 2 validation
        await asyncio.sleep(0.1) # Simulate inference time
        return SpeechTranscribed(text="mock english speech", language="en", confidence=0.92)
