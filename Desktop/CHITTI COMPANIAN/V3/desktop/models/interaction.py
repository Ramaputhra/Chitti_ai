from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from desktop.models.events import DomainEvent

@dataclass(frozen=True)
class InteractionEnvelope(DomainEvent):
    """
    Immutable representation of an external intent.
    Assigned a UUID by the transport layer for end-to-end tracing.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    origin: str = ""
    transport: str = ""
    session_id: str = ""
    user_id: str = "local_user"
    payload: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

@dataclass(frozen=True)
class IntentResult:
    """
    Structured semantic intent extracted by the AIRuntime.
    """
    intent: str
    confidence: float
    parameters: Dict[str, Any]
    source: str
    interaction_id: str
    model: str = "unknown"

@dataclass(frozen=True)
class IntentResolved(DomainEvent):
    """
    Published by ConversationRuntime after resolving natural language.
    """
    result: IntentResult
    id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    event_type: str = "INTENT_RESOLVED"
    version: str = "1.0"

class ExpressionType(Enum):
    SPEAK = "SPEAK"
    DISPLAY = "DISPLAY"
    NOTIFY = "NOTIFY"
    COMMAND = "COMMAND"

@dataclass
class ExpressionRequested(DomainEvent):
    """
    Requested by the Execution Runtime (via capabilities).
    The Expression Runtime will render this request into a RenderedExpression.
    """
    interaction_id: str = ""
    correlation_id: str = ""
    expression_type: ExpressionType = ExpressionType.SPEAK
    payload: Any = None
    emotion: str = "NEUTRAL"
    priority: str = "NORMAL"
    modality_preference: str = "text"

@dataclass(frozen=True)
class RenderedExpression:
    """
    Final output decided by the Expression Runtime.
    Routed to the OutputTransport for display/playback.
    """
    interaction_id: str
    rendered_text: str
    rendered_audio: bytes = b""
    transport_target: str = ""
