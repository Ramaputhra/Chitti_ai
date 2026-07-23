from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class ProviderState(Enum):
    UNKNOWN = "UNKNOWN"
    OFFLINE = "OFFLINE"
    CONNECTING = "CONNECTING"
    READY = "READY"
    BUSY = "BUSY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"

class RetryPolicy(Enum):
    NONE = "NONE"
    SAFE = "SAFE"
    IDEMPOTENT = "IDEMPOTENT"

class ProviderType(Enum):
    CLOUD = "CLOUD"
    LAN = "LAN"
    MCP = "MCP"

@dataclass
class ProviderCapabilities:
    tool_calling: bool = False
    structured_output: bool = False
    json_mode: bool = False
    vision: bool = False
    speech: bool = False
    embedding: bool = False
    reranking: bool = False
    reasoning: bool = False
    streaming: bool = False
    batch: bool = False
    max_context: int = 8192
    max_output: int = 4096

@dataclass
class RemoteProviderManifest:
    provider_id: str
    display_name: str
    provider_type: ProviderType
    api_base: str
    requires_api_key: bool
    capabilities: ProviderCapabilities
    supported_models: List[str] = field(default_factory=list)
    priority: int = 100

@dataclass
class RemoteRequest:
    service: str
    payload: Dict[str, Any]
    runtime_context: Dict[str, Any]
    priority: int = 1
    privacy: str = "LOW"
    retry_policy: RetryPolicy = RetryPolicy.NONE
    stream: bool = False
    timeout: int = 30
