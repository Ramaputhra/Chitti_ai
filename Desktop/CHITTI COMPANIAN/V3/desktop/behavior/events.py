from dataclasses import dataclass
from desktop.models.events import SystemEvent
from desktop.behavior.models import BehaviorProfile
from desktop.behavior.context import EmotionState
from desktop.behavior.emotion_models import BehaviorTrigger

@dataclass
class EmotionChanged(SystemEvent):
    event_type: str = "EmotionChanged"
    previous: EmotionState = EmotionState.IDLE
    current: EmotionState = EmotionState.IDLE
    reason: BehaviorTrigger = BehaviorTrigger.SYSTEM_ALERT
    trace_id: str = ""
    timestamp: float = 0.0

@dataclass
class BehaviorProfileChanged(SystemEvent):
    event_type: str = "BehaviorProfileChanged"
    profile: BehaviorProfile = None

@dataclass
class BehaviorModeChanged(SystemEvent):
    event_type: str = "BehaviorModeChanged"
    previous_mode: str = ""
    new_mode: str = ""

@dataclass
class NarrationLevelChanged(SystemEvent):
    event_type: str = "NarrationLevelChanged"
    previous_level: str = ""
    new_level: str = ""

@dataclass
class InteractionModeChanged(SystemEvent):
    event_type: str = "InteractionModeChanged"
    previous_mode: str = ""
    new_mode: str = ""
