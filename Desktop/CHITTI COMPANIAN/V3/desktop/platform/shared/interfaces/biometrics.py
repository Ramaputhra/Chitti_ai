from typing import List, Protocol
from desktop.platform.shared.models.biometrics import SpeakerState
from desktop.platform.shared.interfaces.provider import IProvider

class ISpeakerVerifier(IProvider):
    """
    Identifies the speaker from an audio chunk but does not authorize them.
    (See Rule 14: The Audio Runtime identifies speakers but never authenticates users.)
    """
    def extract_embedding(self, audio_data: bytes) -> List[float]:
        ...
        
    def verify(self, audio_data: bytes, reference_embeddings: List[List[float]]) -> SpeakerState:
        ...
