from dataclasses import dataclass, field
from typing import Dict, List, Any
from desktop.models.environment import EnvironmentSession, WorkspaceState

@dataclass
class IDESession(EnvironmentSession):
    """
    Rule 358: IDE sessions own workspace state. Engines never persist project state.
    """
    workspace_id: str = ""
    opened_editors: List[str] = field(default_factory=list)
    terminal_ids: List[str] = field(default_factory=list)
    cursor_history: List[Dict[str, Any]] = field(default_factory=list)
    selection_history: List[Dict[str, Any]] = field(default_factory=list)
    debug_state: Dict[str, Any] = field(default_factory=dict)
    git_context: Dict[str, str] = field(default_factory=dict)
    language_context: Dict[str, str] = field(default_factory=dict)

class IDESessionManager:
    """
    Scaffold for IDE Session Recovery hooks.
    Valuable for when long-running coding tasks are interrupted.
    """
    def restore_workspace(self, workspace_id: str) -> IDESession:
        pass
        
    def restore_terminal(self, terminal_id: str):
        pass
        
    def restore_debug_session(self, debug_id: str):
        pass
