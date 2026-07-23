from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Intent:
    """
    Standardized interpretation of the user's desire.
    Produced by the Intent Engine and consumed by the Action Planner.
    """
    type: str  # e.g., "Greeting", "Identity", "Command"
    confidence: float
    entities: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
