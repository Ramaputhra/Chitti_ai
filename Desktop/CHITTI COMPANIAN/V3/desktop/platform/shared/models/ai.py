import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class ModelLifecycle(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    DISCOVERING = "DISCOVERING"
    DOWNLOADING = "DOWNLOADING"
    INSTALLING = "INSTALLING"
    READY = "READY"
    BUSY = "BUSY"
    FAILED = "FAILED"
    UNLOADED = "UNLOADED"

@dataclass(frozen=True)
class AIExecutionMetrics:
    conversation_id: str
    request_id: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    ttft_ms: float
    generation_ms: float
    tool_calls: int
    planner_latency_ms: float
    inference_latency_ms: float
    total_latency_ms: float



@dataclass(frozen=True)
class ConversationContext:
    desktop_state: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    emotion: str
    time: str
    memory: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Prompt:
    system_prompt: str
    developer_prompt: str
    safety_prompt: str
    memory_context: str
    desktop_context: str
    tool_descriptions: str
    conversation: str
    user_message: str

    def compile(self) -> str:
        return "\n\n".join(
            filter(
                None,
                [
                    self.system_prompt,
                    self.developer_prompt,
                    self.safety_prompt,
                    self.memory_context,
                    self.desktop_context,
                    self.tool_descriptions,
                    self.conversation,
                    self.user_message,
                ],
            )
        )


@dataclass(frozen=True)
class LLMRequest:
    prompt: Prompt
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = True


@dataclass(frozen=True)
class ToolInvocation:
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    confidence: float
    source: str
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    tool_invocations: List[ToolInvocation] = field(default_factory=list)
    latency_ms: float = 0.0
    finish_reason: str = "stop"
    raw_json: Optional[str] = None
    schema_version: int = 1


class ToolResultStatus(Enum):
    PARTIAL = "PARTIAL"
    FINAL = "FINAL"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ToolResult:
    status: ToolResultStatus
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionPlan:
    steps: List[ToolInvocation]
    requires_confirmation: bool = False
    priority: int = 1
    timeout_sec: float = 30.0


@dataclass(frozen=True)
class ResponseChunk:
    text: str
    is_final: bool = False
