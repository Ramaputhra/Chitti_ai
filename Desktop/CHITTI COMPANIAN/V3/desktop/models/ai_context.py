import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RuntimeContext:
    """
    Context injected into every Provider Adapter execution.
    Contains operational constraints and metadata, completely isolating
    the provider from global state or conversation history.
    """
    device: str = "cpu"  # cpu, gpu, npu
    quantization: str = "fp32"  # fp16, int8, int4
    timeout_ms: int = 5000
    priority: int = 0  # 0 = normal, 1 = high (e.g. Wake Word), -1 = background
    cancellation_token: bool = False  # Checked periodically during long inference
    tracing_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Optional telemetry callback (func(trace_id, event, metrics))
    # Passed as a string placeholder here for structure, but in practice
    # this might be a weakref or an event bus channel.
    telemetry_channel: Optional[str] = None
