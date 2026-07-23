from dataclasses import dataclass, field
import time
from typing import Dict, Any

class SystemEvent:
    event_type: str = "SystemEvent"
    
Event = SystemEvent

class DomainEvent(SystemEvent):
    event_type: str = "DomainEvent"
    
@dataclass
class KernelShutdownRequest(SystemEvent):
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class PlanCreated(SystemEvent):
    plan: Any = None
    timestamp: Any = None
    source: str = ""
    correlation_id: str = ""
    domain: str = ""
    action: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionCompletedEvent(SystemEvent):
    timestamp: Any = None
    source: str = ""
    correlation_id: str = ""
    event_type: str = "EXECUTION_COMPLETED"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EventMetadata:
    timestamp: float = field(default_factory=time.time)
    publisher: str = "unknown"
    trace_id: str = "unknown"

@dataclass
class ContextPayload:
    workflow_id: str = "none"
    conversation_id: str = "default_convo"
    speaker_id: str = "unknown"
    language: str = "en"
    authentication: str = "none"

@dataclass(frozen=True)
class EventEnvelope:
    """
    Rule 247: Wraps immutable business events with mutable infrastructure context.
    """
    event: SystemEvent
    context: ContextPayload = field(default_factory=ContextPayload)
    metadata: EventMetadata = field(default_factory=EventMetadata)
