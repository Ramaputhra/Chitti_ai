from dataclasses import dataclass
from desktop.models.events import SystemEvent

@dataclass
class SpeechTranscribed(SystemEvent):
    event_type: str = "SpeechTranscribed"
    text: str = ""
    language: str = "en"
    confidence: float = 0.0

@dataclass
class SpeakerVerified(SystemEvent):
    event_type: str = "SpeakerVerified"
    speaker_id: str = ""
    confidence: float = 0.0
    authenticated: bool = False
