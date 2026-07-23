from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

class PlanStatus(Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SUPERSEDED = "SUPERSEDED"
    CANCELLED = "CANCELLED"

@dataclass(frozen=True)
class PlanConstraint:
    constraint_id: str
    description: str
    is_hard_constraint: bool

@dataclass(frozen=True)
class PlanOutcome:
    """The declarative expectation of what happens when a step finishes."""
    expected_state: str
    expected_artifacts: List[str] 

@dataclass(frozen=True)
class PlanDecision:
    """Models branching paths in a plan without execution logic."""
    decision_id: str
    condition_description: str
    true_path_step_id: Optional[str]
    false_path_step_id: Optional[str]

@dataclass(frozen=True)
class PlanDependency:
    predecessor_step_id: str
    successor_step_id: str

@dataclass(frozen=True)
class PlanStep:
    step_id: str
    description: str
    action_intent: str # Semantic intent, NOT a capability name. Mapped by Workflow Translator.
    constraints: List[PlanConstraint]
    decision: Optional[PlanDecision]
    expected_outcome: PlanOutcome

@dataclass(frozen=True)
class PlanMetadata:
    planner_version: str
    created_at: datetime
    generated_from_goal_version: str

@dataclass(frozen=True)
class Plan:
    plan_id: str
    goal_id: str
    supersedes_plan_id: Optional[str] # Lineage graph mapping replans
    steps: List[PlanStep]
    dependencies: List[PlanDependency]
    global_constraints: List[PlanConstraint]
    metadata: PlanMetadata

@dataclass(frozen=True)
class PlanExecution:
    """Mutable execution state extracted from the immutable Plan contract."""
    plan_id: str
    status: PlanStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    current_step_id: Optional[str]

class ReplanningFailureCategory(Enum):
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    KNOWLEDGE_INSUFFICIENT = "KNOWLEDGE_INSUFFICIENT"
    CAPABILITY_FAILURE = "CAPABILITY_FAILURE"
    POLICY_BLOCKED = "POLICY_BLOCKED"
    USER_ABORTED = "USER_ABORTED"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"

@dataclass(frozen=True)
class ReplanningDirective:
    """Explicit policy constraints for the next planning iteration."""
    failure_category: ReplanningFailureCategory
    avoid_capability_ids: List[str]
    required_heuristics: List[str]
    adjusted_constraints: List[str]
    max_retries_exceeded: bool

from desktop.models.goals import GoalContext

@dataclass(frozen=True)
class PlanningContext:
    """The complete wrapper of planning facts and planning policy."""
    goal_context: GoalContext
    replanning_directive: Optional[ReplanningDirective]
