from dataclasses import dataclass
from typing import Dict, Any, Optional
from desktop.models.environment import EnvironmentSession

@dataclass
class DesktopSession(EnvironmentSession):
    """
    Owns OS automation context, avoiding caching the full desktop state.
    """
    active_window_id: Optional[str] = None
    focused_application: Optional[str] = None
    active_monitor: int = 0
    cursor_position: Optional[Dict[str, int]] = None
    clipboard_snapshot: Optional[str] = None
    active_workspace: Optional[str] = None
