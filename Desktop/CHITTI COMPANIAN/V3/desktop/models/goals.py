from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any

class GoalState(Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"

class GoalPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    BACKGROUND = 1

@dataclass(frozen=True)
class GoalCriterion:
    criterion_id: str
    description: str
    required: bool
    status: bool

@dataclass(frozen=True)
class Goal:
    """
    Rule 221 & 222: A Goal defines ONLY the desired outcome. 
    It never embeds context, active knowledge references, or execution state.
    """
    goal_id: str
    description: str
    priority: GoalPriority
    state: GoalState
    created_at: datetime
    deadline: Optional[datetime]
    criteria: List[GoalCriterion]

class GoalRelationshipType(Enum):
    PARENT_OF = "PARENT_OF"
    DEPENDS_ON = "DEPENDS_ON"
    BLOCKS = "BLOCKS"
    DUPLICATES = "DUPLICATES"
    SUPPORTS = "SUPPORTS"

@dataclass(frozen=True)
class GoalRelationship:
    source_goal_id: str
    target_goal_id: str
    relationship_type: GoalRelationshipType

@dataclass(frozen=True)
class ContextMetadata:
    assembled_at: datetime
    knowledge_version: str
    goal_version: str
    pipeline_version: str

@dataclass(frozen=True)
class GoalContext:
    """
    Transient evaluation context assembled dynamically for a goal.
    This prevents the Goal from owning or locking into specific knowledge versions.
    """
    goal_id: str
    metadata: ContextMetadata
    relevant_knowledge: List[str] # List of UUIDs 
    active_constraints: List[str] # List of constraint IDs or descriptions
    pending_tasks: List[str]
    related_goals: List[str]

@dataclass(frozen=True)
class GoalSession:
    """
    Transient execution state for a Goal, containing the runtime plans and snapshot.
    """
    goal_id: str
    context: GoalContext
    selected_tasks: List[str]
    active_workflows: List[str]
    planner_snapshot: dict
