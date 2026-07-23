from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class ResponseMode(Enum):
    CHAT = "CHAT"
    SUMMARIZE = "SUMMARIZE"
    EXPLAIN = "EXPLAIN"
    PLAN = "PLAN"
    REWRITE = "REWRITE"
    CODE = "CODE"
    VISION = "VISION"

class ContextPriority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1

@dataclass
class PromptContext:
    system_rules: str = ""
    session_context: str = ""
    working_memory: List[str] = field(default_factory=list)
    recent_messages: List[str] = field(default_factory=list)
    current_input: str = ""

@dataclass
class PromptMetadata:
    version: str = "1.0"
    content_hash: str = ""
    template_name: str = ""

@dataclass
class ContextItem:
    priority: ContextPriority
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class CapabilityResultItem(ContextItem):
    id: str = ""
    status: str = "success"
    
@dataclass
class InferenceRequest:
    system_persona: str
    user_message: str
    planner_goal: str
    response_mode: ResponseMode = ResponseMode.CHAT
    memory_context: List[ContextItem] = field(default_factory=list)
    awareness_context: List[ContextItem] = field(default_factory=list)
    capability_results: List[CapabilityResultItem] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 1024

@dataclass
class ReasonTrace:
    planner_goal: str
    retrieval_ids: List[str] = field(default_factory=list)
    capability_ids: List[str] = field(default_factory=list)
    memory_ids: List[str] = field(default_factory=list)
    awareness_ids: List[str] = field(default_factory=list)

@dataclass
class InferenceTelemetry:
    provider: str
    model: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cached: bool
    temperature: float
    finish_reason: str
    grounding_score: Optional[float] = None
    error: Optional[str] = None

class ProviderHealth(Enum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"

class CapabilityStatus(Enum):
    NATIVE = "NATIVE"
    EXPERIMENTAL = "EXPERIMENTAL"
    UNSUPPORTED = "UNSUPPORTED"

class CapabilityType(Enum):
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"
    STREAMING = "STREAMING"
    MULTIMODAL = "MULTIMODAL"
    FUNCTION_CALLING = "FUNCTION_CALLING"

@dataclass
class CapabilityMetadata:
    status: CapabilityStatus
    details: str = ""

@dataclass
class ProviderCapabilities:
    capabilities: Dict[CapabilityType, CapabilityMetadata]
    max_context: int
    is_local: bool

@dataclass
class ProviderInfo:
    name: str
    model: str
    capabilities: ProviderCapabilities

@dataclass
class InferenceResponse:
    content: str
    model_used: str
    latency_ms: float
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class InferenceResult:
    response: InferenceResponse
    intent: Optional[str] = None
    confidence: float = 0.0
