from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum

class WidgetCategory(Enum):
    MEDIA = "MEDIA"
    COMMUNICATION = "COMMUNICATION"
    SYSTEM = "SYSTEM"
    PRODUCTIVITY = "PRODUCTIVITY"
    AUTOMATION = "AUTOMATION"
    PRESENTATION = "PRESENTATION"
    VISION = "VISION"
    UTILITY = "UTILITY"

@dataclass
class WidgetManifest:
    manifest_version: str = "1.0.0"
    widget_version: str = "1.0.0"
    widget_id: str = "default_widget"
    display_name: str = "Default Widget"
    category: str = "UTILITY"
    version: str = "1.0.0"  # Alias for backward compatibility
    description: str = "Canonical CHITTI Desktop Widget"
    supported_runtime_sessions: List[str] = field(default_factory=list)
    default_attachment: str = "CHARACTER_ANCHOR"
    preferred_window_layer: str = "CHARACTER_WIDGET"
    render_profile: str = "WIDGET"
    theme: str = "Dark"
    supports_compact: bool = True
    supports_expanded: bool = True
    supports_notifications: bool = True
    supports_hot_reload: bool = True
    icon: str = "default_icon.svg"
    accent_color: str = "#89B4FA"
    minimum_size: Dict[str, int] = field(default_factory=lambda: {"w": 280, "h": 160})
    preferred_size: Dict[str, int] = field(default_factory=lambda: {"w": 360, "h": 240})
