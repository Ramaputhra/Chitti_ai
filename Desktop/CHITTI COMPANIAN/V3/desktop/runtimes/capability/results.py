from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    TIMED_OUT = "TIMED_OUT"
    CANCELLED = "CANCELLED"

class ExecutionErrorCode(str, Enum):
    ACCESS_DENIED = "ACCESS_DENIED"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    TIMEOUT = "TIMEOUT"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

@dataclass
class ExecutionResult:
    """Strongly typed model encapsulating capability execution results."""
    status: ExecutionStatus
    outputs: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    verification_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[ExecutionErrorCode] = None
    retryable: bool = False
