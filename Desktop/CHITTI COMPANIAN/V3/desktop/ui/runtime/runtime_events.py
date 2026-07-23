from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class UIEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class WindowCreated(UIEvent):
    def __init__(self, timestamp: float, window_id: str, window_type: str):
        super().__init__("WindowCreated", timestamp, {"window_id": window_id, "window_type": window_type})

class WindowDestroyed(UIEvent):
    def __init__(self, timestamp: float, window_id: str):
        super().__init__("WindowDestroyed", timestamp, {"window_id": window_id})

class WindowShown(UIEvent):
    def __init__(self, timestamp: float, window_id: str):
        super().__init__("WindowShown", timestamp, {"window_id": window_id})

class WindowHidden(UIEvent):
    def __init__(self, timestamp: float, window_id: str):
        super().__init__("WindowHidden", timestamp, {"window_id": window_id})

class WindowMoved(UIEvent):
    def __init__(self, timestamp: float, window_id: str, x: int, y: int):
        super().__init__("WindowMoved", timestamp, {"window_id": window_id, "x": x, "y": y})

class WindowDocked(UIEvent):
    def __init__(self, timestamp: float, window_id: str, dock_edge: str):
        super().__init__("WindowDocked", timestamp, {"window_id": window_id, "dock_edge": dock_edge})

class WindowUndocked(UIEvent):
    def __init__(self, timestamp: float, window_id: str):
        super().__init__("WindowUndocked", timestamp, {"window_id": window_id})

class WindowFocused(UIEvent):
    def __init__(self, timestamp: float, window_id: str):
        super().__init__("WindowFocused", timestamp, {"window_id": window_id})

class WindowBlurred(UIEvent):
    def __init__(self, timestamp: float, window_id: str):
        super().__init__("WindowBlurred", timestamp, {"window_id": window_id})

class OverlayShown(UIEvent):
    def __init__(self, timestamp: float, overlay_id: str):
        super().__init__("OverlayShown", timestamp, {"overlay_id": overlay_id})

class OverlayHidden(UIEvent):
    def __init__(self, timestamp: float, overlay_id: str):
        super().__init__("OverlayHidden", timestamp, {"overlay_id": overlay_id})

class NotificationShown(UIEvent):
    def __init__(self, timestamp: float, notification_id: str, title: str):
        super().__init__("NotificationShown", timestamp, {"notification_id": notification_id, "title": title})

class NotificationHidden(UIEvent):
    def __init__(self, timestamp: float, notification_id: str):
        super().__init__("NotificationHidden", timestamp, {"notification_id": notification_id})
