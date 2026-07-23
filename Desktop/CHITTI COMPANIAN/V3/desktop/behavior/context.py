from enum import Enum
from dataclasses import dataclass
from typing import Optional
from desktop.behavior.models import BehaviorProfile, NarrationLevel

class EmotionState(Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    WORKING = "WORKING"
    WAITING = "WAITING"
    CONFIDENT = "CONFIDENT"
    UNSURE = "UNSURE"
    CURIOUS = "CURIOUS"
    PLAYFUL = "PLAYFUL"
    PROUD = "PROUD"
    SORRY = "SORRY"
    CELEBRATING = "CELEBRATING"
    ALERT = "ALERT"

@dataclass(frozen=True)
class BehaviorContext:
    """Shared state across the entire Behavior Layer pipeline."""
    trace_id: str
    conversation_id: str
    language: str
    behavior_profile: BehaviorProfile
    current_emotion: EmotionState
    narration_level: NarrationLevel
    workflow_id: Optional[str] = None

@dataclass(frozen=True)
class DialogueIntent:
    """Intermediary semantic payload from Narration to Character."""
    intent_type: str  # e.g., "START_TASK", "APOLOGY"
    tone: str         # e.g., "PLAYFUL"
    importance: str   # e.g., "LOW", "HIGH"

@dataclass(frozen=True)
class FinalDialogue:
    """The absolute final synthesized response to be passed to TTS and Expression."""
    text: str
    language: str
    voice_profile: str
    pace: str
    emotion: str
    volume: float
