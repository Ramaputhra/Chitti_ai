import logging
from typing import Dict, Optional, List
from desktop.ui.runtime.widgets.base_widget import BaseWidget, UISession
from desktop.ui.runtime.widgets.generic_widget import GenericWidget

logger = logging.getLogger(__name__)

class WidgetManager:
    """
    S36D: Widget Manager owning all 17 generic widget lifecycles & session bindings.
    """
    WIDGET_TYPES = [
        "Media", "Reminder", "Alarm", "Email", "Browser", "Navigation",
        "Presentation", "Printer", "Download", "Upload", "Vision",
        "Clipboard", "Battery", "Weather", "Productivity", "System", "Timer"
    ]

    def __init__(self):
        self.widgets: Dict[str, BaseWidget] = {}

    def create_widget(self, widget_id: str, widget_type: str) -> BaseWidget:
        widget = GenericWidget(widget_id=widget_id, widget_type=widget_type)
        widget.initialize()
        self.widgets[widget_id] = widget
        logger.info(f"[WidgetManager] Created {widget_type} widget '{widget_id}'")
        return widget

    def bind_session(self, widget_id: str, session: UISession):
        if widget_id in self.widgets:
            self.widgets[widget_id].bind_session(session)
            logger.info(f"[WidgetManager] Widget '{widget_id}' bound to session '{session.session_id}' ({session.session_type})")

    def get_widget(self, widget_id: str) -> Optional[BaseWidget]:
        return self.widgets.get(widget_id)

    def close_widget(self, widget_id: str):
        if widget_id in self.widgets:
            self.widgets[widget_id].close()
            del self.widgets[widget_id]
            logger.info(f"[WidgetManager] Closed widget '{widget_id}'")
