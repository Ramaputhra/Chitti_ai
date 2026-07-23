from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List

class SessionState(Enum):
    IDLE = "IDLE"
    ACTIVE_SESSION = "ACTIVE_SESSION"
    WAITING_FOR_REPLY = "WAITING_FOR_REPLY"

@dataclass
class ConversationSessionStartedEvent:
    conversation_id: str
    timestamp: float

@dataclass
class ConversationSessionEndedEvent:
    conversation_id: str
    reason: str  # "timeout", "explicit_close", etc.
    timestamp: float

@dataclass
class ConversationTurnStartedEvent:
    conversation_id: str
    turn_id: str
    source: str # "voice", "text"
    user_input: str
    timestamp: float

@dataclass
class ConversationTurnCompletedEvent:
    conversation_id: str
    turn_id: str
    response_text: str
    capabilities_executed: List[str] = field(default_factory=list)
    timestamp: float = 0.0
