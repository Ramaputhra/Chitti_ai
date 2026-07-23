from dataclasses import dataclass
from typing import Optional

@dataclass
class EntityID:
    """
    A globally unique, permanent identifier for a resolved semantic entity.
    """
    type: str
    id: str


@dataclass
class EntityResolutionStatus:
    """
    Status of an entity's identity resolution process.
    """
    status: str  # "resolved" or "unresolved"
    entity_id: Optional[str] = None
    confidence: float = 0.0
