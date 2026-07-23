import asyncio
from abc import ABC, abstractmethod
from desktop.speech.models import SpeakerVerified

class ISpeakerVerifier(ABC):
    @abstractmethod
    async def enroll(self, audio_chunk: bytes) -> None:
        """Enroll the owner's voice print from the given audio."""
        pass

    @abstractmethod
    async def verify(self, audio_chunk: bytes) -> SpeakerVerified:
        """Verify the given audio against the enrolled voice print."""
        pass

class ECAPATDNNVerifier(ISpeakerVerifier):
    def __init__(self):
        # Placeholder for speechbrain ECAPA-TDNN initialization
        self._enrolled_embedding = None

    async def enroll(self, audio_chunk: bytes) -> None:
        # In a real implementation, convert audio_chunk to tensor and extract embedding
        self._enrolled_embedding = "mock_embedding"

    async def verify(self, audio_chunk: bytes) -> SpeakerVerified:
        # In a real implementation, compare extracted embedding with self._enrolled_embedding
        # Fallback true for mock implementation if enrolled
        if not self._enrolled_embedding:
            return SpeakerVerified(speaker_id="unknown", confidence=0.0, authenticated=False)
            
        return SpeakerVerified(speaker_id="owner", confidence=0.95, authenticated=True)
