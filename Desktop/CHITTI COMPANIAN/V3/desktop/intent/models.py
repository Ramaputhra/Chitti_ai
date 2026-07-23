from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from desktop.models.events import SystemEvent

@dataclass
class IntentMetadata:
    requires_confirmation: bool = False
    requires_authentication: bool = False
    supports_background: bool = True
    supports_parallel: bool = True

@dataclass(frozen=True)
class IntentDefinition:
    intent_id: str
    category: str
    version: int = 1
    priority: int = 0
    metadata: IntentMetadata = field(default_factory=IntentMetadata)
    aliases: list = field(default_factory=list)

@dataclass
class IntentTrace:
    original_text: str = ""
    normalized_text: str = ""
    matched_intent: str = ""
    confidence: float = 0.0
    resolved_entities: Dict[str, Any] = field(default_factory=dict)
    registry_source: str = "core"

@dataclass(frozen=True)
class IntentRecognized(SystemEvent):
    event_type: str = "IntentRecognized"
    intent_id: str = ""
    intent_hash: str = ""
    category: str = ""
    metadata: IntentMetadata = field(default_factory=IntentMetadata)
    entities: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    source: str = "core"
    language: str = "en"
    duration_ms: float = 0.0
    trace: Optional[IntentTrace] = None

@dataclass
class IntentClarificationRequired(SystemEvent):
    event_type: str = "IntentClarificationRequired"
    intent_id: str = ""
    prompt: str = ""
    
@dataclass
class IntentUnknown(SystemEvent):
    event_type: str = "IntentUnknown"
    text: str = ""
