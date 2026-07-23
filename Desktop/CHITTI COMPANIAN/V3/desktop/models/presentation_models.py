from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

class PresentationPriority(Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

class PresenceState(Enum):
    ACTIVE = "ACTIVE"
    FOLLOW_UP_WINDOW = "FOLLOW_UP_WINDOW"
    TASK_EXECUTION = "TASK_EXECUTION"
    EDGE_DOCKED_WORKING = "EDGE_DOCKED_WORKING"
    EDGE_DOCKED_IDLE = "EDGE_DOCKED_IDLE"
    RELAXED_IDLE = "RELAXED_IDLE"
    GOODBYE = "GOODBYE"
    RESIDENT_MODE = "RESIDENT_MODE"

@dataclass
class SpeechPersona:
    formal: float = 1.0
    friendly: float = 0.0
    humour: float = 0.0

@dataclass
class PresentationProfile:
    speech_persona: SpeechPersona = field(default_factory=SpeechPersona)
    voice: str = "default"
    animation_level: str = "expressive"
    verbosity: str = "normal"
    sound_effects: bool = True

@dataclass
class ResponseIntent:
    """
    Deterministic meaning mapped from verification, stripped of personality.
    """
    status: str
    message_key: str
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PresentationPolicy:
    voice: bool = False
    avatar_animation: str = "idle"
    sound_effect: Optional[str] = None
    toast: bool = False
    followup_window: bool = False
    allow_interrupt: bool = True
    priority: PresentationPriority = PresentationPriority.NORMAL

@dataclass
class PresentationDecision:
    response_text: str
    language: str
    voice: str
    avatar_animation: str
    expression: str
    sound: Optional[str]
    followup_window: bool
    expand_avatar: bool
    presentation_priority: PresentationPriority

@dataclass
class ResponseCreatedEvent:
    workflow_id: str
    response_intent: ResponseIntent
    timestamp: float

@dataclass
class PresentationStartedEvent:
    workflow_id: str
    decision: PresentationDecision
    timestamp: float

@dataclass
class PresentationCompletedEvent:
    workflow_id: str
    timestamp: float

@dataclass
class PresenceStateChangedEvent:
    old_state: PresenceState
    new_state: PresenceState
    timestamp: float

@dataclass
class FollowUpWindowOpenedEvent:
    workflow_id: str
    timestamp: float
