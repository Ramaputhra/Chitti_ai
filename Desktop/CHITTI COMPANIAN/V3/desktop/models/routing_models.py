from enum import Enum
from dataclasses import dataclass
from typing import Optional
from desktop.models.remote_provider import ProviderState

class ExecutionMode(Enum):
    LOCAL_ONLY = "LOCAL_ONLY"
    PREFER_LOCAL = "PREFER_LOCAL"
    BALANCED = "BALANCED"
    PREFER_REMOTE = "PREFER_REMOTE"

class ExecutionTarget(Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
    OFFLINE_DEGRADED = "OFFLINE_DEGRADED"

@dataclass
class RoutingDecision:
    selected_runtime: str
    selected_provider: str
    reason: str
    fallback_allowed: bool
    provider_state: ProviderState
    estimated_latency: int
    decision_confidence: float

@dataclass
class RoutingTrace:
    request_id: str
    service: str
    selected_runtime: str
    selected_provider: str
    decision_reason: str
    decision_confidence: float
    execution_time_ms: int
    status: str
