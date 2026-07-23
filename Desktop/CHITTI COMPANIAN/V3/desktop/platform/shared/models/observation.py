import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Observation:
    """
    Standardized semantic perception artifact representing a fact about the physical or digital environment.
    """
    source: str
    type: str
    confidence: float
    payload: Any
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
