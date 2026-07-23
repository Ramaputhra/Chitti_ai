from abc import ABC, abstractmethod
from typing import List, Optional
from desktop.speech.models import SpeechTranscribed

class ISTTProvider(ABC):
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Returns the list of language codes this provider supports."""
        pass
        
    @abstractmethod
    async def transcribe_stream(self, audio_chunk: bytes) -> Optional[SpeechTranscribed]:
        """Processes audio bytes and returns a transcription if speech is fully decoded."""
        pass
