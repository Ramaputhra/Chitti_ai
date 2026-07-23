from dataclasses import dataclass
from typing import Dict, Any, List
from desktop.behavior.models import SpeechStyle, HumorLevel
from desktop.behavior.context import EmotionState

# Safe dynamic variables that Character Runtime is allowed to inject
SAFE_VARIABLES: List[str] = [
    "user_name", "app_name", "website", "file_name", "folder_name",
    "device_name", "time_of_day", "remaining_time", "count",
    "language", "city", "battery_percent", "network_name", "date", "weekday"
]

@dataclass(frozen=True)
class ExpressionHint:
    animation_id: str
    intensity: float

@dataclass(frozen=True)
class GestureHint:
    gesture_id: str
    target: str

@dataclass(frozen=True)
class LipSyncHint:
    viseme_sequence: str

@dataclass(frozen=True)
class DialogueTiming:
    pre_delay_ms: float
    post_delay_ms: float

@dataclass(frozen=True)
class DialogueContent:
    text: str
    language: str
    dialogue_id: str
    template_id: str
    placeholders: Dict[str, Any]
    speech_style: SpeechStyle
    humor_level: HumorLevel
    emotion: EmotionState

@dataclass(frozen=True)
class FinalDialogue:
    text: str
    language: str
    voice_profile_id: str
    speech_profile_id: str
    emotion: EmotionState
    dialogue_id: str
    template_id: str
    expression_hint: ExpressionHint
    gesture_hint: GestureHint
    lip_sync_hint: LipSyncHint
    timing_hint: DialogueTiming
