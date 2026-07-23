from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

class WorkflowStatus(Enum):
    COMPLETED_SUCCESSFULLY = "COMPLETED_SUCCESSFULLY"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    FAILED = "FAILED"
    ABORTED = "ABORTED"

@dataclass(frozen=True)
class TaskAssessment:
    """Evaluative judgement of a specific task's execution."""
    task_id: str
    status: TaskStatus
    extracted_outputs: Dict[str, Any]
    error_summary: Optional[str]

@dataclass(frozen=True)
class ExecutionAnomaly:
    """Observations about execution quality rather than hard failures."""
    category: str  # e.g., "retry_storm", "unexpected_ordering", "timeout_cluster"
    description: str
    affected_task_ids: List[str]

@dataclass(frozen=True)
class WorkflowAssessmentMetadata:
    """Reproducibility metadata for the derived assessment."""
    evaluator_version: str
    assessed_at: datetime
    execution_event_count: int
    execution_history_hash: str

@dataclass(frozen=True)
class WorkflowAssessment:
    """The derived analytical result of a Workflow execution."""
    workflow_id: str
    plan_id: str
    status: WorkflowStatus
    metadata: WorkflowAssessmentMetadata
    task_assessments: List[TaskAssessment]
    anomalies: List[ExecutionAnomaly]

class GoalStatus(Enum):
    SATISFIED = "SATISFIED"
    PARTIALLY_SATISFIED = "PARTIALLY_SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    ABANDONED = "ABANDONED"

@dataclass(frozen=True)
class SatisfactionEvaluation:
    score: float
    contributing_criteria: List[str]
    semantic_confidence: Optional[float]
    deterministic_score: float

@dataclass(frozen=True)
class GoalAssessment:
    """The final analytical result of comparing intent to execution reality."""
    goal_id: str
    workflow_id: str
    plan_id: str
    status: GoalStatus
    satisfaction_evaluation: SatisfactionEvaluation
    unmet_constraints: List[str]
    evaluator_reasoning: str
    assessment_timestamp: datetime
    workflow_assessment_hash: str
