from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

class MessageDirection(Enum):
    BACKEND_TO_FRONTEND = "BACKEND_TO_FRONTEND"
    FRONTEND_TO_BACKEND = "FRONTEND_TO_BACKEND"

class FrontendState(Enum):
    """
    Explicit state machine for the frontend connection lifecycle.
    """
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"
    HANDSHAKE = "HANDSHAKE"
    READY = "READY"
    ACTIVE = "ACTIVE"
    RECOVERING = "RECOVERING"
    CLOSED = "CLOSED"

class AckLevel(Enum):
    """
    Explicit progressive acknowledgment levels.
    """
    ACK_RECEIVED = "ACK_RECEIVED"
    ACK_RENDERING = "ACK_RENDERING"
    ACK_VISIBLE = "ACK_VISIBLE"
    ACK_INTERACTIVE = "ACK_INTERACTIVE"
    ACK_FAILED = "ACK_FAILED"

@dataclass
class FrontendProtocolMessage:
    """
    The standard JSON-serializable wire envelope for all CHITTI UI communication.
    Rule 320: This envelope is stable and strictly versioned.
    """
    protocol_version: int
    message_id: str
    correlation_id: str
    timestamp: float
    direction: MessageDirection
    message_type: str
    session_id: Optional[str]
    payload: Dict[str, Any]
