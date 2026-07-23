from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class WorkspaceModel:
    workspace_id: str
    path: str
    active_branch: str
    open_files: List[str]
    has_uncommitted_changes: bool

@dataclass
class GitStatusModel:
    branch: str
    untracked_files: List[str]
    modified_files: List[str]
    staged_files: List[str]
    ahead_commits: int
    behind_commits: int

@dataclass
class TerminalOutputModel:
    session_id: str
    command: str
    output: str
    exit_code: Optional[int]
    is_running: bool

@dataclass
class DiagnosticIssue:
    file: str
    line: int
    message: str
from desktop.models.activity import ActivityMemoryModel

@dataclass
class WorkspaceMemoryModel(ActivityMemoryModel):
    project_path: str = ""
    opened_files: List[str] = field(default_factory=list)
    window_layout: str = ""
    split_layout: str = ""
    running_servers: List[str] = field(default_factory=list)
    recent_git_branches: List[str] = field(default_factory=list)
    recent_commands: List[str] = field(default_factory=list)
    breakpoints: List[str] = field(default_factory=list)
    active_terminal: str = ""
    last_task: str = ""
    last_build_status: str = ""
    last_debug_session: str = ""
    opened_editors: List[str] = field(default_factory=list)

@dataclass
class ProjectProfileModel:
    project_type: str
    language: str
    framework: str
    package_manager: str
    build_command: str
    run_command: str
    test_command: str
    debug_configuration: Dict[str, Any]
    recommended_workspace_layout: str
    environment_variables: Dict[str, str]
    default_experiences: List[str]
