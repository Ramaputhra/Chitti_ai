from enum import Enum
from dataclasses import dataclass

class FailureSeverity(Enum):
    RECOVERABLE = "RECOVERABLE"
    NODE_FATAL = "NODE_FATAL"
    WORKFLOW_FATAL = "WORKFLOW_FATAL"
    SYSTEM_FATAL = "SYSTEM_FATAL"

class RecoveryPolicy(Enum):
    RETRY = "RETRY"
    RESTART_CAPABILITY = "RESTART_CAPABILITY"
    CHECKPOINT_RESTORE = "CHECKPOINT_RESTORE"
    SKIP_NODE = "SKIP_NODE"
    CANCEL_WORKFLOW = "CANCEL_WORKFLOW"
    ESCALATE = "ESCALATE"

@dataclass(frozen=True)
class TimeoutConfig:
    soft_timeout: float
    hard_timeout: float
    absolute_deadline: float
