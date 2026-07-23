from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass(frozen=True)
class PlanningTrace:
    decision_outcome_id: str
    compilation_rules_applied: List[str]

@dataclass(frozen=True)
class ExecutionStep:
    step_id: str
    action_type: str
    payload: dict
    dependencies: List[str]

@dataclass(frozen=True)
class ExecutionPlan:
    plan_id: str
    steps: List[ExecutionStep]
    plan_confidence: float
    is_executable: bool
    evidence_trace: PlanningTrace

@dataclass(frozen=True)
class PlanningSession:
    session_id: str
    source_decision: Any
    dependency_graph_log: Dict[str, Any]
    prerequisite_checks: List[str]
    final_plan: ExecutionPlan
    timestamp: float = field(default_factory=time.time)

class PlanningBudgetExceededException(Exception):
    pass

class InvalidPlanningStateException(Exception):
    pass
