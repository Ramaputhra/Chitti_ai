from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class SpeechEvent:
    event_type: str
    timestamp: float
    speech_id: str
    payload: Dict[str, Any] = field(default_factory=dict)

class SpeechCreated(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str, text: str):
        super().__init__("SpeechCreated", timestamp, speech_id, {"text": text})

class SpeechQueued(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str, priority: str = "NORMAL"):
        super().__init__("SpeechQueued", timestamp, speech_id, {"priority": priority})

class SpeechStarted(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str, duration: float):
        super().__init__("SpeechStarted", timestamp, speech_id, {"duration": duration})

class SpeechPaused(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str):
        super().__init__("SpeechPaused", timestamp, speech_id, {})

class SpeechResumed(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str):
        super().__init__("SpeechResumed", timestamp, speech_id, {})

class SpeechCompleted(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str):
        super().__init__("SpeechCompleted", timestamp, speech_id, {})

class SpeechCancelled(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str, reason: str = "User interrupt"):
        super().__init__("SpeechCancelled", timestamp, speech_id, {"reason": reason})

class SpeechInterrupted(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str, interrupting_speech_id: str):
        super().__init__("SpeechInterrupted", timestamp, speech_id, {"interrupting_speech_id": interrupting_speech_id})

class SpeechFailed(SpeechEvent):
    def __init__(self, timestamp: float, speech_id: str, error: str):
        super().__init__("SpeechFailed", timestamp, speech_id, {"error": error})
