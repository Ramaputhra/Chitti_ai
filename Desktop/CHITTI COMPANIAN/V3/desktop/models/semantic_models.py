from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

class IntentType(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    SEARCH = "SEARCH"
    CREATE = "CREATE"
    DELETE = "DELETE"
    MOVE = "MOVE"
    UNKNOWN = "UNKNOWN"

class AmbiguityReason(Enum):
    UNKNOWN_ACTION = "UNKNOWN_ACTION"
    UNKNOWN_TARGET = "UNKNOWN_TARGET"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MULTIPLE_TARGETS = "MULTIPLE_TARGETS"
    MISSING_PARAMETER = "MISSING_PARAMETER"

@dataclass
class IntentConfidence:
    intent_score: float = 1.0
    entity_score: float = 1.0
    parameter_score: float = 1.0

    @property
    def overall(self) -> float:
        return min(self.intent_score, self.entity_score, self.parameter_score)

@dataclass
class DesktopIntent:
    action: IntentType
    target: Optional[str] = None
    object_type: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    language: str = "en"
    confidence: IntentConfidence = field(default_factory=IntentConfidence)
    
    source_text: str = ""
    normalized_text: str = ""
    session_id: str = ""

@dataclass
class IntentGeneratedEvent:
    desktop_intent: DesktopIntent
    timestamp: float
    session_id: str

@dataclass
class IntentAmbiguousEvent:
    partial_intent: DesktopIntent
    reason: AmbiguityReason
    confidence: IntentConfidence
    session_id: str
