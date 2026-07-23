from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class RobotCommand:
    """
    The permanent execution interface for Robot Expression.
    Ensures that Robot outputs are executed safely and exclusively through the Expression Runtime.
    """
    command_name: str
    priority: int = 0
    duration_ms: int = 0
    cancelable: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
