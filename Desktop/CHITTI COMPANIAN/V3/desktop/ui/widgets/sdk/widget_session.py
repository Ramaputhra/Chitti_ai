from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class WidgetSession:
    """
    S36D-2: Canonical Runtime Session model.
    Widgets bind ONLY to Runtime Sessions.
    """
    session_id: str
    session_type: str        # "Media", "Reminder", "Alarm", "Timer", "Email", "Browser", "Navigation", "Presentation", etc.
    owner_capability: str    # Metadata only
    data: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    progress: float = 0.0

    def update_data(self, delta: Dict[str, Any]):
        self.data.update(delta)

    def close_session(self):
        self.active = False
