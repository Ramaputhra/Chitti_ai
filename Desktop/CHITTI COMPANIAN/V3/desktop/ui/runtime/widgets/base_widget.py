from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class UISession:
    session_id: str
    session_type: str  # "Media", "Reminder", "Alarm", "Download", "Presentation", etc.
    data: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

class BaseWidget(ABC):
    """
    S36D: Canonical Widget Contract for all 17 generic widgets.
    Widgets SHALL represent runtime sessions.
    Widgets SHALL NEVER execute capabilities; they ONLY visualize state.
    """
    def __init__(self, widget_id: str, widget_type: str):
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.session: Optional[UISession] = None
        self.expanded = False
        self.docked = False
        self.visible = False
        self.x = 0
        self.y = 0

    @abstractmethod
    def initialize(self):
        pass

    def bind_session(self, session: UISession):
        self.session = session
        self.visible = session.active

    @abstractmethod
    def update(self, delta_data: Dict[str, Any]):
        pass

    @abstractmethod
    def render(self) -> str:
        """
        Renders HTML/CSS/SVG or structured JSON representation.
        """
        pass

    def expand(self):
        self.expanded = True

    def collapse(self):
        self.expanded = False

    def dock(self, mode: str = "right"):
        self.docked = True

    def undock(self):
        self.docked = False

    def close(self):
        self.visible = False
        if self.session:
            self.session.active = False

    def destroy(self):
        self.close()
        self.session = None
