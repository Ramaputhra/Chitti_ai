from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class AIProfile(str, Enum):
    AUTOMATIC = "automatic"
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    QUALITY = "quality"
    CREATIVE = "creative"
    ROBOT = "robot"
    OFFLINE = "offline"

@dataclass(frozen=True)
class AIRequest:
    id: str
    capability: str
    payload: Any
    profile: AIProfile = AIProfile.AUTOMATIC
    constraints: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    session: Optional[str] = None
    priority: int = 1
    streaming: bool = False
    cancellation_token: Optional[str] = None

@dataclass
class AIResponse:
    request_id: str
    provider: str
    model: str
    status: str
    result: Any
    telemetry: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    latency: float = 0.0
    tokens: int = 0
    confidence: float = 1.0
    finish_reason: Optional[str] = None

@dataclass(frozen=True)
class AIExecutionStrategy:
    id: str
    steps: List[str]  # e.g., ["ocr", "embedding", "reasoning"]
    parallel: bool = False
    timeout: float = 60.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    fallback_policy: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InferencePlanNode:
    priority: int
    model_id: str
    runtime: str
    
@dataclass
class InferencePlan:
    request_id: str
    capability: str
    strategy: AIExecutionStrategy
    nodes: List[InferencePlanNode]
