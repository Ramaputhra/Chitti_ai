from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Mapping

class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    RETRY = "RETRY"
    SKIPPED = "SKIPPED"

class ErrorCategory(Enum):
    RESOURCE_BUSY = "RESOURCE_BUSY"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    INVALID_PARAMETERS = "INVALID_PARAMETERS"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INTERNAL_ERROR = "INTERNAL_ERROR"

@dataclass(frozen=True)
class ExecutionError:
    code: str
    message: str
    category: ErrorCategory
    retryable: bool
    details: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ExecutionMetrics:
    started_at: float = 0.0
    completed_at: float = 0.0
    duration: float = 0.0
    resource_wait_time: float = 0.0

class Permission(Enum):
    FILESYSTEM = "FILESYSTEM"
    MICROPHONE = "MICROPHONE"
    CAMERA = "CAMERA"
    CLIPBOARD = "CLIPBOARD"
    NETWORK = "NETWORK"
    DESKTOP_CONTROL = "DESKTOP_CONTROL"
    PROCESS_CONTROL = "PROCESS_CONTROL"
    REGISTRY = "REGISTRY"
    NOTIFICATIONS = "NOTIFICATIONS"

class CapabilityHealth(Enum):
    READY = "READY"
    INITIALIZING = "INITIALIZING"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    DISABLED = "DISABLED"

class CapabilityLifecycle(Enum):
    DISCOVERED = "DISCOVERED"
    LOADED = "LOADED"
    VALIDATED = "VALIDATED"
    READY = "READY"
    RUNNING = "RUNNING"
    DISPOSING = "DISPOSING"
    DISPOSED = "DISPOSED"

@dataclass(frozen=True)
class ArtifactReference:
    artifact_id: str
    type: str
    mime_type: str
    storage_location: str
    checksum: str

@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    name: str
    version: str
    api_version: str
    author: str
    description: str
    supported_node_types: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    permissions: List[Permission] = field(default_factory=list)
    timeout: int = 30
    retry_policy: Any = None
    tags: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class CapabilityResult:
    outputs: Mapping[str, Any] = field(default_factory=dict)
    artifacts: List[ArtifactReference] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True)
class ExecutionResult:
    node_id: str
    execution_id: str
    status: ExecutionStatus
    output_data: Mapping[str, Any] = field(default_factory=dict)
    error: Optional[ExecutionError] = None
    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
