from dataclasses import dataclass

@dataclass
class InteractionEvent:
    """
    Standard interaction model routed back to the appropriate Experience instance.
    """
    session_id: str
    widget_id: str
    action: str  # copy, pin, select, filter, expand, drill_down, next_page
    payload: dict
    timestamp: float

class InteractionRouter:
    """
    Routes standard InteractionEvents back to the owning Experience.
    """
    def route(self, event: InteractionEvent):
        print(f"[InteractionRouter] Routing action '{event.action}' from widget '{event.widget_id}' in session '{event.session_id}'")
