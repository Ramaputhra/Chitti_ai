from dataclasses import dataclass, field
from typing import Any, Optional, Dict

@dataclass
class CapabilityPayload:
    """Strongly typed abstraction for capability arguments."""
    data: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

@dataclass
class CapabilityContext:
    """
    Isolated context strictly limiting access to system internals.
    """
    logger: Any
    configuration: dict
    telemetry: Any
    
    payload: CapabilityPayload = field(default_factory=CapabilityPayload)
    
    # Optional APIs deferred for future sprints but explicitly declared
    memory_api: Optional[Any] = None
    reasoning_api: Optional[Any] = None
    user_context: Optional[Any] = None
