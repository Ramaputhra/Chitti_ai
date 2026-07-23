import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CursorState:
    """Detailed state of the user's cursor for intent inference."""
    position_x: int = 0
    position_y: int = 0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    hover_target: Optional[str] = None
    focused_control: Optional[str] = None
    pressed_buttons: List[str] = field(default_factory=list)
    drag_state: bool = False


from desktop.platform.shared.models.perception_model import PerceptionModel


@dataclass
class DesktopModel(PerceptionModel):
    """
    The unified domain model built by the Desktop Observation Runtime.
    Represents the digital desktop state.
    """
    capture_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    active_app: Optional[str] = None
    windows: List[Dict[str, Any]] = field(default_factory=list)
    clipboard: str = ""
    notifications: List[Dict[str, Any]] = field(default_factory=list)
    selection: str = ""
    cursor: CursorState = field(default_factory=CursorState)
    timestamp: float = field(default_factory=time.time)
