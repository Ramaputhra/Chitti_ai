import time
from dataclasses import dataclass, field
from enum import Enum, auto


class SignalType(Enum):
    FREQUENCY = auto()
    RECENCY = auto()
    EXPLICIT_FAVORITE = auto()
    TASK_COMPLETION = auto()
    PROJECT_MEMBERSHIP = auto()
    CALENDAR_RELEVANCE = auto()
    CONTACT_RANK = auto()


@dataclass
class SignificanceSignal:
    type: SignalType
    value: float
    knowledge_id: str  # ID of the Artifact, Entity, or Edge
    timestamp: float = field(default_factory=time.time)
