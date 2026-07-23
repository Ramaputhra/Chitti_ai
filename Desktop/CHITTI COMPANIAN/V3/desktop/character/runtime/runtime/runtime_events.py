from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class RuntimeEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class RuntimeStarted(RuntimeEvent):
    def __init__(self, timestamp: float):
        super().__init__("RuntimeStarted", timestamp, {})

class RuntimeStopped(RuntimeEvent):
    def __init__(self, timestamp: float):
        super().__init__("RuntimeStopped", timestamp, {})

class ClipLoaded(RuntimeEvent):
    def __init__(self, timestamp: float, behavior_id: str, frame_count: int):
        super().__init__("ClipLoaded", timestamp, {"behavior_id": behavior_id, "frame_count": frame_count})

class ClipStarted(RuntimeEvent):
    def __init__(self, timestamp: float, behavior_id: str):
        super().__init__("ClipStarted", timestamp, {"behavior_id": behavior_id})

class ClipCompleted(RuntimeEvent):
    def __init__(self, timestamp: float, behavior_id: str):
        super().__init__("ClipCompleted", timestamp, {"behavior_id": behavior_id})

class TransitionStarted(RuntimeEvent):
    def __init__(self, timestamp: float, from_behavior: str, to_behavior: str):
        super().__init__("TransitionStarted", timestamp, {"from": from_behavior, "to": to_behavior})

class TransitionCompleted(RuntimeEvent):
    def __init__(self, timestamp: float, transition_id: str):
        super().__init__("TransitionCompleted", timestamp, {"transition_id": transition_id})

class PlaybackPaused(RuntimeEvent):
    def __init__(self, timestamp: float):
        super().__init__("PlaybackPaused", timestamp, {})

class PlaybackResumed(RuntimeEvent):
    def __init__(self, timestamp: float):
        super().__init__("PlaybackResumed", timestamp, {})

class PlaybackInterrupted(RuntimeEvent):
    def __init__(self, timestamp: float, current_behavior: str, new_behavior: str):
        super().__init__("PlaybackInterrupted", timestamp, {"current": current_behavior, "new": new_behavior})
