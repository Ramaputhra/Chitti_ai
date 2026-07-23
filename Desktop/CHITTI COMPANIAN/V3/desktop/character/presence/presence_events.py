from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum

class PresenceStateEnum(Enum):
    SYSTEM_TRAY = "SYSTEM_TRAY"
    WAKE = "WAKE"
    CHARACTER_WINDOW = "CHARACTER_WINDOW"
    PRESENCE_DOT = "PRESENCE_DOT"

@dataclass
class PresenceLifecycleEvent:
    event_type: str
    timestamp: float
    state: PresenceStateEnum
    payload: Dict[str, Any] = field(default_factory=dict)

class PresenceStateChanged(PresenceLifecycleEvent):
    def __init__(self, timestamp: float, from_state: PresenceStateEnum, to_state: PresenceStateEnum):
        super().__init__("PresenceStateChanged", timestamp, to_state, {"from_state": from_state.value, "to_state": to_state.value})

class SystemTrayEntered(PresenceLifecycleEvent):
    def __init__(self, timestamp: float):
        super().__init__("SystemTrayEntered", timestamp, PresenceStateEnum.SYSTEM_TRAY, {})

class WokenFromTray(PresenceLifecycleEvent):
    def __init__(self, timestamp: float, wake_source: str = "wake_word"):
        super().__init__("WokenFromTray", timestamp, PresenceStateEnum.WAKE, {"wake_source": wake_source})

class WokenFromDot(PresenceLifecycleEvent):
    def __init__(self, timestamp: float):
        super().__init__("WokenFromDot", timestamp, PresenceStateEnum.WAKE, {})

class CharacterWindowTransformedToDot(PresenceLifecycleEvent):
    def __init__(self, timestamp: float):
        super().__init__("CharacterWindowTransformedToDot", timestamp, PresenceStateEnum.PRESENCE_DOT, {})

class DotTransformedToTray(PresenceLifecycleEvent):
    def __init__(self, timestamp: float):
        super().__init__("DotTransformedToTray", timestamp, PresenceStateEnum.SYSTEM_TRAY, {})

class PresentationModeEntered(PresenceLifecycleEvent):
    def __init__(self, timestamp: float):
        super().__init__("PresentationModeEntered", timestamp, PresenceStateEnum.PRESENCE_DOT, {})

class PresentationModeExited(PresenceLifecycleEvent):
    def __init__(self, timestamp: float):
        super().__init__("PresentationModeExited", timestamp, PresenceStateEnum.CHARACTER_WINDOW, {})
