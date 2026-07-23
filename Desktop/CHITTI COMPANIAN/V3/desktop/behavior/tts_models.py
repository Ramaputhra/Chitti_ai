from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
from desktop.behavior.character_models import FinalDialogue

class AudioChannel(Enum):
    SPEECH = "SPEECH"
    NOTIFICATION = "NOTIFICATION"
    UI = "UI"
    MEDIA = "MEDIA"

class InterruptPolicy(Enum):
    NONE = "NONE"
    SOFT = "SOFT"
    IMMEDIATE = "IMMEDIATE"

@dataclass(frozen=True)
class VoiceProfile:
    profile_id: str
    language: str
    provider: str
    voice: str
    sample_rate: int
    pitch: float
    speed: float
    emotion_support: bool
    streaming_support: bool

@dataclass(frozen=True)
class SpeechSession:
    speech_id: str
    dialogue_id: str
    trace_id: str
    started_at: float
    finished_at: Optional[float] = None
    cancelled: bool = False

@dataclass(frozen=True)
class VisemeEvent:
    time_offset_ms: float
    viseme_id: str  # e.g., 'Neutral', 'A', 'E', 'Closed'

@dataclass(frozen=True)
class VisemeTimeline:
    speech_id: str
    events: List[VisemeEvent]

@dataclass(frozen=True)
class SpeechQueueItem:
    dialogue: FinalDialogue
    priority: int
    interrupt_policy: InterruptPolicy
    expiry_time: float
    speech_reaction_delay_ms: float
