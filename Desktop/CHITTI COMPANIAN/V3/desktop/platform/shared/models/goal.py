from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import uuid
import time

class GoalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    ABANDONED = "ABANDONED"

class ProjectStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"

class GoalSessionState(str, Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"

class AssignmentSource(str, Enum):
    USER = "USER"
    PLANNER = "PLANNER"
    RULE = "RULE"
    IMPORT = "IMPORT"

@dataclass
class Project:
    name: str
    description: str = ""
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class Goal:
    name: str
    description: str = ""
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = None
    status: GoalStatus = GoalStatus.ACTIVE
    
    # Progress Metrics
    estimated_minutes: float = 0.0
    tracked_minutes: float = 0.0
    completion_percentage: float = 0.0
    last_activity: Optional[float] = None
    
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class WorkspaceMapping:
    workspace_key: str
    target_id: str  # Can be project_id or goal_id
    target_type: str # "PROJECT" or "GOAL"
    mapping_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    confidence: float = 1.0
    assignment_source: AssignmentSource = AssignmentSource.PLANNER
    created_at: float = field(default_factory=time.time)

@dataclass
class GoalSession:
    goal_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    tracked_seconds: float = 0.0
    state: GoalSessionState = GoalSessionState.ACTIVE

    @property
    def duration(self) -> float:
        return self.tracked_seconds

