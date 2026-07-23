from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time

from desktop.models.intent import SessionTimeline
from desktop.models.browser import BrowserContext

class SessionState(Enum):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    FINALIZING = "FINALIZING"
    COMMITTED = "COMMITTED"

@dataclass
class ClipboardEvent:
    timestamp: float
    application: str
    content_preview: str
    content_hash: str
    content_type: str
    character_count: int

@dataclass
class TerminalEvent:
    timestamp: float
    shell: str
    cwd: str
    command: str
    duration_sec: float
    exit_code: int

@dataclass
class SessionStatistics:
    duration_sec: float = 0.0
    application_count: int = 0
    document_count: int = 0
    focus_switches: int = 0

@dataclass
class WorkSession:
    id: str
    start_time: float
    end_time: Optional[float] = None
    state: SessionState = SessionState.CREATING
    
    primary_project: Optional[str] = None
    confidence: float = 0.0
    
    activities: set = field(default_factory=set)
    intent: str = "Unknown"
    intent_confidence: float = 0.0
    timeline: SessionTimeline = field(default_factory=SessionTimeline)
    
    applications: set = field(default_factory=set)
    documents: set = field(default_factory=set)
    directories: set = field(default_factory=set)
    terminals: set = field(default_factory=set)
    
    # Store raw (timestamp, app, title) to calculate reading duration
    active_windows: List[tuple] = field(default_factory=list)
    
    clipboard_events: List[ClipboardEvent] = field(default_factory=list)
    terminal_events: List[TerminalEvent] = field(default_factory=list)
    
    # Fallback/hints for real-time before SQLite extraction
    browser_title_hints: set = field(default_factory=set)
    
    browser_context: Optional[BrowserContext] = None
    
    aliases: set = field(default_factory=set)
    display_layout: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    statistics: SessionStatistics = field(default_factory=SessionStatistics)
    
    def pause(self):
        if self.state == SessionState.ACTIVE:
            self.state = SessionState.PAUSED
            
    def resume(self):
        if self.state == SessionState.PAUSED:
            self.state = SessionState.ACTIVE
            
    def finalize(self):
        self.state = SessionState.FINALIZING
        self.end_time = time.time()
        self.statistics.duration_sec = self.end_time - self.start_time
        self.statistics.application_count = len(self.applications)
        self.statistics.document_count = len(self.documents)
