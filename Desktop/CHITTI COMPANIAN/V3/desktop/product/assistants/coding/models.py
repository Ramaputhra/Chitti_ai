from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class WorkspaceSnapshot:
    """Rich understanding of the development environment."""
    editor: str
    tabs: List[str]
    terminal: str
    git: str
    diagnostics: List[str]
    breakpoints: List[str]
    tests: str
    running_processes: List[str]

@dataclass
class CodingSession:
    """The working context for the Coding Assistant."""
    project: str
    workspace: WorkspaceSnapshot
    branch: str
    active_files: List[str]
    related_files: List[str]
    terminal_state: str
    git_state: str
    recent_changes: str
    unfinished_tasks: List[str]

@dataclass
class DetectedGoal:
    """Implicit or explicit user goal deduced from evidence."""
    goal: str
    confidence: float
    evidence: List[str]
    alternatives: Dict[str, float]
    missing_information: List[str]
