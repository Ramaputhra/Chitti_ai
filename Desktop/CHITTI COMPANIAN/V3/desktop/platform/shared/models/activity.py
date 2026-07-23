from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import uuid
import hashlib

class ActivitySessionState(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    RESUMED = "RESUMED"
    ENDED = "ENDED"
    PERSISTED = "PERSISTED"

class ActivityCategory(str, Enum):
    UNKNOWN = "UNKNOWN"
    IDE = "IDE"
    BROWSER = "BROWSER"
    DOCUMENT = "DOCUMENT"
    TERMINAL = "TERMINAL"
    CHAT = "CHAT"
    DESIGN = "DESIGN"
    MEDIA = "MEDIA"
    SYSTEM = "SYSTEM"

class ActivitySource(str, Enum):
    DESKTOP = "DESKTOP"
    BROWSER = "BROWSER"
    TERMINAL = "TERMINAL"
    MOBILE = "MOBILE"
    API = "API"
    SYSTEM = "SYSTEM"

class ActivityEndedReason(str, Enum):
    SWITCH = "SWITCH"
    SHUTDOWN = "SHUTDOWN"
    LOCK = "LOCK"
    SLEEP = "SLEEP"
    LOGOFF = "LOGOFF"
    CRASH = "CRASH"
    TIMEOUT = "TIMEOUT"


@dataclass
class ActivitySession:
    """
    Represents a historical, continuous period of work or interaction.
    Unlike WorldState which is the current snapshot, an ActivitySession is immutable once ended and persisted.
    """
    activity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: ActivitySessionState = ActivitySessionState.CREATED
    source: ActivitySource = ActivitySource.DESKTOP
    confidence: float = 1.0
    
    # Core identifying fields
    app_name: str = ""
    window_title: Optional[str] = None
    workspace: Optional[str] = None
    category: ActivityCategory = ActivityCategory.UNKNOWN
    
    # Timing
    start_time: float = 0.0
    end_time: Optional[float] = None
    ended_reason: Optional[ActivityEndedReason] = None
    
    # Future enrichments (populated by Goal/Project Runtimes later)
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    interrupted_by: Optional[str] = None
    switch_reason: Optional[str] = None
    
    # We delay computation of workspace_key until runtime supplies values
    workspace_key: Optional[str] = None

    @property
    def duration(self) -> float:
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return 0.0

    def generate_workspace_key(self, project_root: str = "", document_path: str = "") -> str:
        """
        Generates a stable BLAKE2s hash based on workspace identity, NOT transient window titles.
        """
        payload = f"{self.source.value}:{self.app_name}:{self.workspace}:{project_root}:{document_path}"
        self.workspace_key = hashlib.blake2s(payload.encode("utf-8"), digest_size=16).hexdigest()
        return self.workspace_key

    def to_dict(self) -> dict:
        return {
            "activity_id": self.activity_id,
            "state": self.state.value,
            "source": self.source.value,
            "confidence": self.confidence,
            "app_name": self.app_name,
            "window_title": self.window_title,
            "workspace": self.workspace,
            "category": self.category.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "ended_reason": self.ended_reason.value if self.ended_reason else None,
            "project_id": self.project_id,
            "goal_id": self.goal_id,
            "interrupted_by": self.interrupted_by,
            "switch_reason": self.switch_reason,
            "workspace_key": self.workspace_key
        }
