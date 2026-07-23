from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class UIEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class WidgetOpened(UIEvent):
    def __init__(self, timestamp: float, widget_id: str, session_id: str):
        super().__init__("WidgetOpened", timestamp, {"widget_id": widget_id, "session_id": session_id})

class WidgetClosed(UIEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetClosed", timestamp, {"widget_id": widget_id})

class WidgetUpdated(UIEvent):
    def __init__(self, timestamp: float, widget_id: str, state_summary: Dict[str, Any]):
        super().__init__("WidgetUpdated", timestamp, {"widget_id": widget_id, "state": state_summary})

class WidgetExpanded(UIEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetExpanded", timestamp, {"widget_id": widget_id})

class WidgetCollapsed(UIEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetCollapsed", timestamp, {"widget_id": widget_id})

class WidgetDocked(UIEvent):
    def __init__(self, timestamp: float, widget_id: str, dock_mode: str):
        super().__init__("WidgetDocked", timestamp, {"widget_id": widget_id, "dock_mode": dock_mode})

class WidgetUndocked(UIEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetUndocked", timestamp, {"widget_id": widget_id})

class NotificationShown(UIEvent):
    def __init__(self, timestamp: float, notification_id: str, title: str):
        super().__init__("NotificationShown", timestamp, {"notification_id": notification_id, "title": title})

class NotificationDismissed(UIEvent):
    def __init__(self, timestamp: float, notification_id: str):
        super().__init__("NotificationDismissed", timestamp, {"notification_id": notification_id})

class DialogOpened(UIEvent):
    def __init__(self, timestamp: float, dialog_id: str, title: str):
        super().__init__("DialogOpened", timestamp, {"dialog_id": dialog_id, "title": title})

class DialogClosed(UIEvent):
    def __init__(self, timestamp: float, dialog_id: str):
        super().__init__("DialogClosed", timestamp, {"dialog_id": dialog_id})
