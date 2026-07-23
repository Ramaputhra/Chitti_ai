from enum import Enum
from dataclasses import dataclass, field
from typing import List

class InteractionMode(Enum):
    PROACTIVE = "PROACTIVE"
    ASSISTIVE = "ASSISTIVE"
    REACTIVE = "REACTIVE"
    STEALTH = "STEALTH"

class NarrationLevel(Enum):
    NONE = 0
    MINIMAL = 1
    NORMAL = 2
    VERBOSE = 3
    DEBUG = 4

class SpeechStyle(Enum):
    FORMAL = "FORMAL"
    CASUAL = "CASUAL"
    PLAYFUL = "PLAYFUL"
    RESPECTFUL = "RESPECTFUL"
    ENERGETIC = "ENERGETIC"

class ConversationStyle(Enum):
    BRIEF = "BRIEF"
    BALANCED = "BALANCED"
    DETAILED = "DETAILED"

class HumorLevel(Enum):
    NONE = "NONE"
    LIGHT = "LIGHT"
    NORMAL = "NORMAL"
    HIGH = "HIGH"

class ResponsePace(Enum):
    FAST = "FAST"
    NORMAL = "NORMAL"
    THOUGHTFUL = "THOUGHTFUL"

class CelebrationLevel(Enum):
    NONE = "NONE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class CompanionPresenceLevel(Enum):
    QUIET = "QUIET"
    BALANCED = "BALANCED"
    COMPANION = "COMPANION"
    ENTHUSIASTIC = "ENTHUSIASTIC"

@dataclass(frozen=True)
class BehaviorProfile:
    profile_id: str
    behavior_version: str
    voice_profile_id: str
    
    narration_level: NarrationLevel
    interaction_mode: InteractionMode
    presence_level: CompanionPresenceLevel
    
    speech_style: SpeechStyle
    conversation_style: ConversationStyle
    humor_level: HumorLevel
    response_pace: ResponsePace
    celebration_level: CelebrationLevel
    
    animation_level: float
    emotion_level: float
    
    supported_capabilities: List[str] = field(default_factory=list)

@dataclass
class BehaviorState:
    """The volatile state of the behavior engine, driven by the static profile."""
    current_emotion: str = "IDLE"
    is_speaking: bool = False
    is_animating: bool = False
