from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from desktop.models.activity import ActivityMemoryModel
from desktop.models.companion import UniversalActionItem

class MeetingLifecycle(Enum):
    SCHEDULED = "Scheduled"
    PREPARING = "Preparing"
    READY = "Ready"
    IN_MEETING = "In Meeting"
    FOLLOW_UP = "Follow-up"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

class MeetingHealth(Enum):
    HEALTHY = "Healthy"
    NEEDS_PREPARATION = "Needs Preparation"
    MISSING_CONTEXT = "Missing Context"
    RUNNING_LATE = "Running Late"
    FOLLOW_UP_REQUIRED = "Follow-up Required"

@dataclass
class MeetingGoal:
    description: str = ""
    progress: str = "Pending"
    outcome: str = ""
    next_step: str = ""

@dataclass
class MeetingMemoryModel(ActivityMemoryModel):
    meeting_id: str = ""
    participants: List[str] = field(default_factory=list)
    agenda: str = ""
    related_documents: List[str] = field(default_factory=list)
    related_emails: List[str] = field(default_factory=list)
    conversation_links: List[str] = field(default_factory=list)
    notes: str = ""
    decisions: List[str] = field(default_factory=list)
    action_items: List[UniversalActionItem] = field(default_factory=list)
    meeting_lifecycle: MeetingLifecycle = MeetingLifecycle.SCHEDULED
    meeting_health: MeetingHealth = MeetingHealth.HEALTHY
    meeting_goal: Optional[MeetingGoal] = None
