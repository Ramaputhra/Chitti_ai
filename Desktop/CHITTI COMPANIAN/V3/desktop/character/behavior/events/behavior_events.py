from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class BehaviorEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class WakewordDetected(BehaviorEvent):
    def __init__(self, timestamp: float, keyword: str = "CHITTI"):
        super().__init__("WakewordDetected", timestamp, {"keyword": keyword})

class SpeechStarted(BehaviorEvent):
    def __init__(self, timestamp: float, speech_id: str, duration: float):
        super().__init__("SpeechStarted", timestamp, {"speech_id": speech_id, "duration": duration})

class SpeechCompleted(BehaviorEvent):
    def __init__(self, timestamp: float, speech_id: str):
        super().__init__("SpeechCompleted", timestamp, {"speech_id": speech_id})

class SentenceBoundary(BehaviorEvent):
    def __init__(self, timestamp: float, index: int):
        super().__init__("SentenceBoundary", timestamp, {"index": index})

class PhraseBoundary(BehaviorEvent):
    def __init__(self, timestamp: float, index: int):
        super().__init__("PhraseBoundary", timestamp, {"index": index})

class Pause(BehaviorEvent):
    def __init__(self, timestamp: float, duration: float):
        super().__init__("Pause", timestamp, {"duration": duration})

class ExecutionStarted(BehaviorEvent):
    def __init__(self, timestamp: float, workflow_id: str):
        super().__init__("ExecutionStarted", timestamp, {"workflow_id": workflow_id})

class ExecutionCompleted(BehaviorEvent):
    def __init__(self, timestamp: float, workflow_id: str, status: str = "SUCCESS"):
        super().__init__("ExecutionCompleted", timestamp, {"workflow_id": workflow_id, "status": status})

class ReminderTriggered(BehaviorEvent):
    def __init__(self, timestamp: float, reminder_id: str):
        super().__init__("ReminderTriggered", timestamp, {"reminder_id": reminder_id})

class ReminderCompleted(BehaviorEvent):
    def __init__(self, timestamp: float, reminder_id: str):
        super().__init__("ReminderCompleted", timestamp, {"reminder_id": reminder_id})

class PresentationStarted(BehaviorEvent):
    def __init__(self, timestamp: float, presentation_id: str):
        super().__init__("PresentationStarted", timestamp, {"presentation_id": presentation_id})

class PresentationCompleted(BehaviorEvent):
    def __init__(self, timestamp: float, presentation_id: str):
        super().__init__("PresentationCompleted", timestamp, {"presentation_id": presentation_id})

class NavigationStarted(BehaviorEvent):
    def __init__(self, timestamp: float, destination: str):
        super().__init__("NavigationStarted", timestamp, {"destination": destination})

class NavigationCompleted(BehaviorEvent):
    def __init__(self, timestamp: float, destination: str):
        super().__init__("NavigationCompleted", timestamp, {"destination": destination})

class VisionStarted(BehaviorEvent):
    def __init__(self, timestamp: float, target: str):
        super().__init__("VisionStarted", timestamp, {"target": target})

class VisionCompleted(BehaviorEvent):
    def __init__(self, timestamp: float, target: str):
        super().__init__("VisionCompleted", timestamp, {"target": target})

class BrowserOpened(BehaviorEvent):
    def __init__(self, timestamp: float, url: str):
        super().__init__("BrowserOpened", timestamp, {"url": url})

class BrowserClosed(BehaviorEvent):
    def __init__(self, timestamp: float):
        super().__init__("BrowserClosed", timestamp, {})
