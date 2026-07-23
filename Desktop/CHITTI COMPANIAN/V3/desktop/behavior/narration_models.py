from enum import Enum
from dataclasses import dataclass
from desktop.behavior.context import EmotionState
from desktop.behavior.emotion_models import BehaviorTrigger

class CommunicationMode(Enum):
    SILENT = "SILENT"
    SPEAK = "SPEAK"
    TEXT_ONLY = "TEXT_ONLY"
    VISUAL_ONLY = "VISUAL_ONLY"
    SPEAK_AND_VISUAL = "SPEAK_AND_VISUAL"
    QUEUE = "QUEUE"

class CommunicationPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class SuppressionReason(Enum):
    NONE = "NONE"
    USER_IS_SPEAKING = "USER_IS_SPEAKING"
    USER_TYPING = "USER_TYPING"
    MIC_ACTIVE = "MIC_ACTIVE"
    ANOTHER_DIALOG_ACTIVE = "ANOTHER_DIALOG_ACTIVE"
    DO_NOT_DISTURB = "DO_NOT_DISTURB"
    BACKGROUND_TASK = "BACKGROUND_TASK"
    RATE_LIMITED = "RATE_LIMITED"
    PRESENCE_SILENCED = "PRESENCE_SILENCED"

@dataclass(frozen=True)
class CommunicationIntent:
    intent_id: str
    modality: CommunicationMode
    tone: EmotionState
    priority: CommunicationPriority
    trigger: BehaviorTrigger
    reason: str
    workflow_id: str
    trace_id: str
