from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class WidgetEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class WidgetRegistered(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str, display_name: str):
        super().__init__("WidgetRegistered", timestamp, {"widget_id": widget_id, "display_name": display_name})

class WidgetLoaded(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetLoaded", timestamp, {"widget_id": widget_id})

class WidgetAttached(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str, attachment_type: str):
        super().__init__("WidgetAttached", timestamp, {"widget_id": widget_id, "attachment_type": attachment_type})

class WidgetDetached(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetDetached", timestamp, {"widget_id": widget_id})

class WidgetExpanded(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetExpanded", timestamp, {"widget_id": widget_id})

class WidgetCollapsed(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetCollapsed", timestamp, {"widget_id": widget_id})

class WidgetUpdated(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str, state_summary: Dict[str, Any]):
        super().__init__("WidgetUpdated", timestamp, {"widget_id": widget_id, "state": state_summary})

class WidgetDestroyed(WidgetEvent):
    def __init__(self, timestamp: float, widget_id: str):
        super().__init__("WidgetDestroyed", timestamp, {"widget_id": widget_id})
