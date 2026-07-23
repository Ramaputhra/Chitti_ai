import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

class ExecutionStatus(Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"
    CANCELLED = "Cancelled"
    RETRYING = "Retrying"

@dataclass
class ExecutionResult:
    """
    The strict output of a capability execution (Rule 42).
    """
    status: ExecutionStatus
    output: Any = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StepExecutionRecord:
    """
    Immutable historical record of a step execution attempt (Rule 25 refinement).
    """
    step_id: str
    attempt: int
    status: ExecutionStatus
    started_at: float
    finished_at: float
    result: ExecutionResult
