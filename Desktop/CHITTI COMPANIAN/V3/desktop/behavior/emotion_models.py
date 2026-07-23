from enum import Enum
from dataclasses import dataclass
from desktop.behavior.context import EmotionState

class BehaviorTrigger(Enum):
    USER_LISTENING = "USER_LISTENING"
    USER_SPEAKING = "USER_SPEAKING"
    TASK_STARTED = "TASK_STARTED"
    TASK_PROGRESS = "TASK_PROGRESS"
    TASK_WAITING = "TASK_WAITING"
    TASK_RESUMED = "TASK_RESUMED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    TASK_CANCELLED = "TASK_CANCELLED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    USER_CONFIRMED = "USER_CONFIRMED"
    USER_DECLINED = "USER_DECLINED"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    IDLE_TIMEOUT = "IDLE_TIMEOUT"
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_ENDED = "SESSION_ENDED"

class EmotionCategory(Enum):
    WORKING = "WORKING"
    SOCIAL = "SOCIAL"
    ERROR = "ERROR"
    WAITING = "WAITING"
    IDLE = "IDLE"

@dataclass(frozen=True)
class EmotionSnapshot:
    state: EmotionState
    intensity: float
    trigger: BehaviorTrigger
    transition_time: float
    expires_at: float

@dataclass(frozen=True)
class TimelineEntry:
    timestamp: float
    trigger: BehaviorTrigger
    old_state: EmotionState
    new_state: EmotionState
    duration: float
