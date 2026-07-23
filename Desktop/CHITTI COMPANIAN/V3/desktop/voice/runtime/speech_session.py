from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class SpeechSessionState(Enum):
    CREATED = "Created"
    QUEUED = "Queued"
    SYNTHESIZING = "Synthesizing"
    READY = "Ready"
    PLAYING = "Playing"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    FAILED = "Failed"

@dataclass
class SpeechSession:
    speech_id: str
    session_id: str
    text_narration: str
    language: str = "en-US"
    voice_profile: str = "friendly_female"
    speech_style: str = "Friendly"
    state: SpeechSessionState = SpeechSessionState.CREATED
    created_at: float = 0.0
    audio_path: Optional[str] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
