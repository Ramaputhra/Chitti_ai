from dataclasses import dataclass
from desktop.models.events import SystemEvent

@dataclass
class SpeechStarted(SystemEvent):
    event_type: str = "SpeechStarted"
    speech_id: str = ""
    dialogue_id: str = ""
    trace_id: str = ""

@dataclass
class SpeechPaused(SystemEvent):
    event_type: str = "SpeechPaused"
    speech_id: str = ""
    reason: str = ""

@dataclass
class SpeechResumed(SystemEvent):
    event_type: str = "SpeechResumed"
    speech_id: str = ""

@dataclass
class SpeechInterrupted(SystemEvent):
    event_type: str = "SpeechInterrupted"
    speech_id: str = ""
    interrupted_by: str = ""

@dataclass
class SpeechCompleted(SystemEvent):
    event_type: str = "SpeechCompleted"
    speech_id: str = ""
    trace_id: str = ""
