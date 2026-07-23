from dataclasses import dataclass
from typing import Optional, Generic, TypeVar

T = TypeVar('T')

@dataclass
class InferenceMetadata:
    """
    Operational telemetry from a physical execution backend.
    """
    model_id: str
    provider_backend: str
    latency_ms: float
    cached: bool
    tokens: Optional[int] = None
    error: Optional[str] = None

@dataclass
class AIResult(Generic[T]):
    """
    The standard response envelope from the AI Runtime to the Caller.
    Separates the domain-specific payload from operational telemetry.
    """
    payload: T
    confidence: float
    metadata: InferenceMetadata
