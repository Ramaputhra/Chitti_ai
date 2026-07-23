import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional


class PriorityLevel(Enum):
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    IGNORE = auto()


@dataclass
class Priority:
    """
    Expressive priority object assigned to an AttentionEvent by the AttentionEngine.
    """
    level: PriorityLevel
    reason: str
    expiration: float  # Absolute timestamp when this priority expires
    interrupt_allowed: bool
    requires_planner: bool
    confidence: float


@dataclass
class AttentionEvent:
    """
    The standardized event contract passed through the entire system.
    All raw inputs (Vision, Desktop, Robot) are normalized into this format.
    """
    source: str
    category: str
    target: str
    payload: Dict[str, Any]
    priority: Optional[Priority] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
