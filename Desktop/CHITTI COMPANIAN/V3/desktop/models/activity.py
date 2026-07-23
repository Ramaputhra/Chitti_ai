from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class ActivitySession:
    """
    Mutable session state tracking an ongoing activity.
    Owned exclusively by Activity Intelligence Engine.
    """
    session_id: str
    activity_type: str
    start_time: datetime
    last_update: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    related_observations: List[str] = field(default_factory=list)
    workspace_hint: Optional[str] = None
    confidence: float = 1.0

@dataclass(frozen=True)
class ActivityEvent:
    """
    Immutable finalized output emitted when an ActivitySession closes.
    Consumed by MemoryRuntime or VerificationRuntime.
    """
    activity_id: str
    activity_type: str
    start_time: datetime
    end_time: datetime
    duration: float
    related_observations: List[str]
    workspace_hint: Optional[str]
    confidence: float

from desktop.models.conversation import ConversationArtifact

@dataclass
class ActivityArtifact(ConversationArtifact):
    """A higher-order semantic artifact representing a user's behavioral goal."""
    activity_type: str
    supporting_artifacts: List[str]
    confidence: float
    focus_application: str

@dataclass
class WorkflowArtifact(ActivityArtifact):
    workflow_name: str
    cross_app_context: bool
    active_participants: List[str]

@dataclass
class TaskArtifact(ActivityArtifact):
    task_description: str
    parent_workflow_id: str

@dataclass
class ProgressArtifact(ActivityArtifact):
    momentum_state: str  # STALLED, IN_PROGRESS, COMPLETED
    completion_estimate: str
    blockers: List[str]
