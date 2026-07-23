from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from abc import ABC

# ---------------------------------------------------------
# Foundational Primitives
# ---------------------------------------------------------
class ActionItemPriority(Enum):
    URGENT = "Urgent"
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"

class ActionItemStatus(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DEFERRED = "Deferred"

@dataclass
class UniversalActionItem:
    title: str
    source: str
    priority: ActionItemPriority = ActionItemPriority.NORMAL
    status: ActionItemStatus = ActionItemStatus.PENDING
    deadline: Optional[datetime] = None
    related_activity_id: Optional[str] = None

class NotificationSeverity(Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"
    SUCCESS = "Success"

@dataclass
class CompanionNotification:
    title: str
    body: str
    category: str
    severity: NotificationSeverity = NotificationSeverity.INFO
    action: Optional[str] = None
    expires_at: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CompanionInsight:
    title: str
    description: str
    severity: str
    confidence: str
    source: str
    recommended_action: Optional[str] = None

@dataclass
class CompanionArtifact:
    artifact_type: str
    title: str
    source: str
    uri: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    related_session: Optional[str] = None
    related_resources: List[str] = field(default_factory=list)
    related_goal: Optional[str] = None
    related_activity: Optional[str] = None
    created_by: str = "CHITTI"

@dataclass
class CompanionResource:
    resource_id: str = ""
    resource_type: str = ""
    title: str = ""
    uri: str = ""
    source: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DocumentResource(CompanionResource):
    resource_type: str = "Document"
    file_path: str = ""

@dataclass
class EmailResource(CompanionResource):
    resource_type: str = "Email"
    sender: str = ""
    subject: str = ""

@dataclass
class MeetingResource(CompanionResource):
    resource_type: str = "Meeting"
    participants: List[str] = field(default_factory=list)

@dataclass
class ResearchSourceResource(CompanionResource):
    resource_type: str = "ResearchSource"
    domain: str = ""

@dataclass
class GitRepositoryResource(CompanionResource):
    resource_type: str = "GitRepository"
    branch: str = ""

@dataclass
class PDFResource(CompanionResource):
    resource_type: str = "PDF"
    pages: int = 1

@dataclass
class TimelineEvent:
    timestamp: datetime
    event_type: str
    description: str
    reference_id: str

@dataclass
class CompanionTimeline:
    events: List[TimelineEvent] = field(default_factory=list)

@dataclass
class CompanionGoal:
    title: str
    description: str
    progress: int # 0-100
    status: str
    priority: str
    origin: str # 'Meeting', 'Research', 'Coding'
    related_session: str
    due_date: Optional[datetime] = None

@dataclass
class CompanionWorkspace:
    windows: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    documents: List[str] = field(default_factory=list)
    browser_tabs: List[str] = field(default_factory=list)
    presentation: str = ""
    layout: str = ""
    session_id: str = ""

# ---------------------------------------------------------
# Strongly Typed Domain Data
# ---------------------------------------------------------
@dataclass
class CompanionDomainData(ABC):
    domain: str

@dataclass
class CodingDomainData(CompanionDomainData):
    domain: str = "Coding"
    git_branch: str = ""
    open_files: List[str] = field(default_factory=list)

@dataclass
class MeetingDomainData(CompanionDomainData):
    domain: str = "Meeting"
    participants: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)

@dataclass
class ResearchDomainData(CompanionDomainData):
    domain: str = "Research"
    sources: List[str] = field(default_factory=list)
    knowledge_map_id: str = ""

@dataclass
class DocumentDomainData(CompanionDomainData):
    domain: str = "Document"
    active_page: int = 1
    highlights: List[str] = field(default_factory=list)

# ---------------------------------------------------------
# Activity Memory (Unified)
# ---------------------------------------------------------
class ActivityState(Enum):
    ACTIVE = "Active"
    PAUSED = "Paused"
    INTERRUPTED = "Interrupted"
    FINISHED = "Finished"
    FAILED = "Failed"

@dataclass
class ObserverStatus:
    observer: str
    healthy: bool
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ActivityMemoryModel:
    activity_id: str
    domain: str
    application: str
    workspace_path: str
    project_name: str
    launch_command: str
    readiness: str
    browser_url: str
    git_branch: str
    last_active: datetime
    resume_priority: int
    verification: Dict[str, Any] = field(default_factory=dict)
    
    # Production Hardening Fields (V1.1)
    state: ActivityState = ActivityState.PAUSED
    resume_confidence: float = 1.0
    observer_health: List[ObserverStatus] = field(default_factory=list)
    schema_version: int = 1
    
    goals: List[CompanionGoal] = field(default_factory=list)

# ---------------------------------------------------------
# Core Session Management
# ---------------------------------------------------------
@dataclass
class SessionProfile:
    layout: str
    applications: List[str]
    presentation: str
    observers: List[str]
    knowledge_sources: List[str]
    automation: List[str]
    startup_actions: List[str]
    shutdown_actions: List[str]
    verification_level: str

class CompanionState(Enum):
    IDLE = "Idle"
    PREPARING = "Preparing"
    WAITING = "Waiting"
    EXECUTING = "Executing"
    OBSERVING = "Observing"
    PAUSED = "Paused"
    COMPLETED = "Completed"

@dataclass
class ExecutionCheckpoint:
    checkpoint_id: str
    orchestrator_state: str
    completed_steps: List[str] = field(default_factory=list)
    running_processes: List[int] = field(default_factory=list) # PIDs
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CompanionContext:
    active_session: str
    active_goal: Optional[str] = None
    active_workspace: Optional[str] = None
    focused_resource: Optional[str] = None
    current_activity: Optional[str] = None
    user_attention: Optional[str] = None

@dataclass
class CompanionSession:
    session_id: str
    session_type: str
    profile: SessionProfile
    state: CompanionState
    active_goal: Optional[CompanionGoal] = None
    current_context: CompanionContext = field(default_factory=lambda: CompanionContext(active_session=""))
    memory: Optional[ActivityMemoryModel] = None
    experience: str = ""
    timeline: CompanionTimeline = field(default_factory=CompanionTimeline)
    observers: List[str] = field(default_factory=list)
    workspace: Optional[CompanionWorkspace] = None
    health: str = "Healthy"

@dataclass
class ParticipantProfile:
    name: str
    organization: str = ""
    role: str = ""
    recent_meetings: List[str] = field(default_factory=list)
    recent_emails: List[str] = field(default_factory=list)
    related_projects: List[str] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    conversation_history: List[str] = field(default_factory=list)
    open_action_items: List[UniversalActionItem] = field(default_factory=list)
