from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from desktop.product.assistants.base import Evidence

class MeetingPhase(Enum):
    PREPARING = 1
    JOINING = 2
    ACTIVE = 3
    WRAPPING_UP = 4
    POST_MEETING = 5
    RETURN_TO_WORK = 6

@dataclass
class ContextTransition:
    """Models transitioning between different user contexts (e.g., Coding -> Meeting -> Coding)."""
    source_context: str
    target_context: str
    preserved_state_id: Optional[str] # ID managed by Continuity Engine
    restoration_plan: List[str]
    confidence: float

@dataclass
class MeetingContext:
    """Combines meeting metadata with current working state."""
    meeting_title: str
    participants: List[str]
    related_topics: List[str]
    related_projects: List[str]
    current_workspace: str # e.g., "Editing models.py in CHITTI"
    expected_decisions: List[str]
    open_questions: List[str]
    time_constraints: str
    importance: str

@dataclass
class MeetingBrief:
    """Prepared before the meeting. The reusable artifact."""
    agenda: str
    participants: List[str]
    previous_decisions: List[str]
    open_questions: List[str]
    relevant_documents: List[str]
    risks: List[str]
    recommended_focus: str

@dataclass
class MeetingTimelineEvent:
    """A point in the meeting timeline."""
    timestamp: datetime
    speaker: str
    decision: Optional[str] = None
    action: Optional[str] = None
    knowledge_change: Optional[str] = None

@dataclass
class MeetingTimeline:
    """Searchable memory of the meeting progression."""
    meeting_id: str
    events: List[MeetingTimelineEvent]

@dataclass
class MeetingOutcome:
    """Produced after the meeting. Feeds back into Knowledge and Memory runtimes."""
    decisions: List[str]
    action_items: List[str]
    new_questions: List[str]
    knowledge_updates: List[str] # Feeds to DecisionTrace / TopicGraph
    followups: List[str]
    affected_projects: List[str]
    confidence: float
