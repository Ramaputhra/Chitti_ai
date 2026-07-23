from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass(frozen=True)
class ExecutionTrace:
    execution_plan_id: str
    compilation_trace: Any

@dataclass(frozen=True)
class ExecutionStepResult:
    step_id: str
    status: str
    stdout: str
    stderr: str
    execution_time_ms: int

@dataclass(frozen=True)
class ExecutionResult:
    result_id: str
    overall_status: str
    step_results: List[ExecutionStepResult]
    execution_confidence: float
    evidence_trace: ExecutionTrace

@dataclass(frozen=True)
class ExecutionSession:
    session_id: str
    source_plan: Any
    monitor_logs: Dict[str, Any]
    final_result: ExecutionResult
    timestamp: float = field(default_factory=time.time)

class ExecutionBudgetExceededException(Exception):
    pass

class InvalidExecutionStateException(Exception):
    pass
