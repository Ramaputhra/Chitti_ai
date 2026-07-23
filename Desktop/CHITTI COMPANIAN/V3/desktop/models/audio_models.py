import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class SpeechState(Enum):
    SLEEPING = "SLEEPING"
    WAKE_DETECTED = "WAKE_DETECTED"
    LISTENING = "LISTENING"
    UNDERSTANDING = "UNDERSTANDING"
    THINKING = "THINKING"
    EXPECTING_REPLY = "EXPECTING_REPLY"

@dataclass
class AudioSession:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.utcnow)
    wake_source: str = "openWakeWord"
    language: Optional[str] = None
    speech_segments: bytearray = field(default_factory=bytearray)
    transcript: Optional[str] = None
    is_active: bool = True
