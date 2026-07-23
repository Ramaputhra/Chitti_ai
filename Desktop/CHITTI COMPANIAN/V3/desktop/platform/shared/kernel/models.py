import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Note: We will import specific Runtimes here once they are refactored into desktop.runtimes
# For now, we use Any to represent the runtimes to avoid circular dependencies during Sprint 14.

@dataclass
class ExecutionResult:
    """
    Universal runtime contract (Rule 29). 
    Every step executed by any runtime must return this structure.
    Runtimes report outcomes; they never determine subsequent actions.
    """
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CancellationToken:
    """
    Used to safely interrupt long-running actions.
    """
    cancelled: bool = False
    reason: Optional[str] = None
    timestamp: Optional[float] = None
    requested_by: Optional[str] = None

    def cancel(self, reason: str, requested_by: str) -> None:
        self.cancelled = True
        self.reason = reason
        self.timestamp = time.time()
        self.requested_by = requested_by


@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable context passed to the Executor.
    Provides isolated access to the necessary runtimes and telemetry,
    without exposing the planner or event bus directly.
    """
    # Correlation Hierarchy
    session_id: str
    conversation_id: str
    workflow_id: str
    step_id: str

    # Runtimes (Typed as Any for now pending Sprint 15-19 refactors)
    capability_runtime: Any
    memory_runtime: Any
    inference_runtime: Any
    expression_runtime: Any
    
    # Telemetry hook for async metric logging
    telemetry_manager: Any
