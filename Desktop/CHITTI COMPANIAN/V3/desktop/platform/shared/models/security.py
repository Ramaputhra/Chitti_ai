from dataclasses import dataclass
from enum import Enum, auto


class PermissionDecision(Enum):
    ALLOW = auto()
    DENY = auto()
    CONFIRM = auto()


@dataclass
class PermissionResult:
    decision: PermissionDecision
    reason: str = ""
