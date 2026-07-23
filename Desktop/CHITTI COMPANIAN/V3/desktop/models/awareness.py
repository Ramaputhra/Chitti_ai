from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time

class AwarenessType(Enum):
    WINDOW = "WINDOW"
    PROCESS = "PROCESS"
    DOWNLOAD = "DOWNLOAD"
    POWER = "POWER"
    NETWORK = "NETWORK"
    USB = "USB"
    SESSION = "SESSION"
    FILE_OPERATION = "FILE_OPERATION"

class AwarenessLevel(Enum):
    LEVEL_1_ALWAYS_ON = 1
    LEVEL_2_USER_REQUESTED = 2
    LEVEL_3_CAPABILITY_REQUESTED = 3

class AwarenessSource(Enum):
    SYSTEM = "SYSTEM"
    USER_REQUEST = "USER_REQUEST"
    CAPABILITY = "CAPABILITY"
    RECOVERY = "RECOVERY"

@dataclass
class AwarenessEvent:
    """
    Records an observation made by the AwarenessRuntime.
    Rule 11 (Observe Before Remember): These are facts, not interpretations.
    """
    id: str
    type: AwarenessType
    level: AwarenessLevel
    source: AwarenessSource
    label: str
    confidence: float
    correlation_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
