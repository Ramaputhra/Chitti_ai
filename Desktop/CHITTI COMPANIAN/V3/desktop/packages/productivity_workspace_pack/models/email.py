from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from desktop.models.companion import CompanionDomainData

class EmailHealth(Enum):
    HEALTHY = "Healthy"
    NEEDS_REPLY = "Needs Reply"
    WAITING_FOR_RESPONSE = "Waiting For Response"
    BLOCKED = "Blocked"
    OVERDUE = "Overdue"

class ConversationLifecycle(Enum):
    THREAD_CREATED = "Thread Created"
    DISCUSSION = "Discussion"
    WAITING = "Waiting"
    ACTION_REQUIRED = "Action Required"
    RESOLVED = "Resolved"
    ARCHIVED = "Archived"

@dataclass
class EmailContextScore:
    urgency: int
    importance: int
    relationship: int
    deadline: int
    recent_activity: int
    project_match: int
    
    @property
    def total_score(self) -> int:
        return self.urgency + self.importance + self.relationship + self.deadline + self.recent_activity + self.project_match

@dataclass
class CompanionCommitment:
    commitment_id: str
    description: str
    due_date: datetime
    status: str = "Pending"
    related_thread_id: str = ""
    recipient: str = ""

@dataclass
class EmailDomainData(CompanionDomainData):
    domain: str = "Email"
    active_thread_id: str = ""
    health: EmailHealth = EmailHealth.HEALTHY
    lifecycle: ConversationLifecycle = ConversationLifecycle.THREAD_CREATED
    context_score: Optional[EmailContextScore] = None
    commitments: List[CompanionCommitment] = field(default_factory=list)
