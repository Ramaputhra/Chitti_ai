from dataclasses import dataclass
from enum import Enum

class ShutdownReason(Enum):
    USER = "user"
    SYSTEM = "system"
    UPDATE = "update"
    CRASH = "crash"
    RESTART = "restart"

@dataclass
class ShutdownRequest:
    """Event payload for requesting a graceful shutdown of the platform."""
    reason: ShutdownReason
    message: str = ""
