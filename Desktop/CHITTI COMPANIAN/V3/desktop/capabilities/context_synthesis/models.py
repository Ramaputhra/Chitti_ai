import enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

class UserWorkIntent(enum.Enum):
    """The synthesized intention of the user (e.g. not just typing, but WRITING)."""
    IMPLEMENTING = "implementing"
    DEBUGGING = "debugging"
    RESEARCHING = "researching"
    WRITING = "writing"
    REVIEWING = "reviewing"
    DESIGNING = "designing"
    MEETING = "meeting"
    BROWSING = "browsing"
    UNKNOWN = "unknown"

@dataclass
class ContextField:
    """A single piece of synthesized context, with confidence and source lineage."""
    value: Any
    confidence: float
    sources: List[str]

@dataclass
class WorkingSet:
    """The active files, tabs, and sessions across the workspace."""
    active_files: List[str] = field(default_factory=list)
    active_tabs: List[str] = field(default_factory=list)
    recent_documents: List[str] = field(default_factory=list)
    terminal_sessions: List[str] = field(default_factory=list)
    browser_tabs: List[str] = field(default_factory=list)

@dataclass
class DesktopContextModel:
    """
    The canonical, high-level semantic representation of what the user is doing.
    Synthesized from World Runtime and secondary extractors.
    """
    current_task: ContextField
    user_work_intent: ContextField # Wraps UserWorkIntent
    current_project: ContextField
    current_document: ContextField
    current_activity: ContextField
    application_stack: ContextField
    workspace: ContextField
    meeting: ContextField
    coding_context: ContextField
    browser_context: ContextField
    working_set: ContextField # Wraps WorkingSet
    estimated_focus: ContextField
    overall_confidence: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ContextDiff:
    """Captures meaningful shifts in context for the Memory Runtime."""
    previous_timestamp: datetime
    current_timestamp: datetime
    task_changed: bool
    intent_changed: bool
    project_changed: bool
    working_set_changes: Dict[str, Any]
    summary_of_change: str
