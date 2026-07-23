from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CapabilityManifest:
    capability_id: str
    semantic_intents: List[str]
    capability_version: str
    required_permissions: List[str]
    supported_parameters: Dict[str, Any]
    return_schema: Dict[str, Any]
    supports_rollback: bool
    default_timeout_ms: int
    is_retryable: bool

class CapabilityLifecycleState:
    REGISTERED = "REGISTERED"
    READY = "READY"
    BUSY = "BUSY"
    FAILED = "FAILED"
    DISABLED = "DISABLED"
