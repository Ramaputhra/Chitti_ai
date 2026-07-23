import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from desktop.platform.shared.models.artifact import Artifact
from desktop.platform.shared.models.session import ConversationSession


@dataclass
class ExecutionTelemetry:
    capability: str
    tool: str
    status: str
    latency_ms: float = 0.0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    exception: Optional[str] = None
    retry_count: int = 0


@dataclass(frozen=True)
class ExecutionContext:
    session: ConversationSession
    user: str
    permissions: List[str]
    timeout_sec: float
    cancellation_token: Any
    telemetry: ExecutionTelemetry
    priority: int = 1
    source: str = "Planner"
    correlation_id: str = ""


class ExecutionStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    PARTIAL = auto()
    CANCELLED = auto()


@dataclass
class ExecutionResult:
    status: ExecutionStatus
    artifacts: List[Artifact] = field(default_factory=list)
    summary: str = ""
    data: Any = None
    telemetry: Optional[ExecutionTelemetry] = None
    next_actions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    presentation: Optional[Any] = None  # Holds PresentationModel
