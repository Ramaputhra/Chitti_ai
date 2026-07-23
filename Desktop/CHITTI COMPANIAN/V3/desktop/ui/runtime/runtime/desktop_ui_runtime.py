import logging
from typing import Optional, List, Dict, Any
from desktop.ui.runtime.runtime.runtime_controller import RuntimeController
from desktop.ui.runtime.widgets.base_widget import BaseWidget, UISession

logger = logging.getLogger(__name__)

class DesktopUIRuntime:
    """
    S36D: Master Desktop UI Runtime & Widget Framework facade.
    The ONLY runtime responsible for rendering: Desktop Notifications, Toasts, Dialogs, Floating Windows,
    Countdowns, Badges, Widgets, Docked Widgets, Character Attached Widgets, and Overlay Windows.
    NEVER executes capabilities. ONLY visualizes runtime sessions.
    Exposes ONLY events to Visual Coordinator.
    """
    def __init__(self):
        self.controller = RuntimeController()
        logger.info("Desktop UI Runtime & Widget Framework initialized cleanly.")

    def start(self):
        self.controller.start()

    def stop(self):
        self.controller.stop()

    def create_widget(self, widget_id: str, widget_type: str, session: UISession) -> BaseWidget:
        return self.controller.create_and_bind_widget(widget_id, widget_type, session)

    def show_notification(self, notification_id: str, title: str, message: str, category: str = "info"):
        return self.controller.notification_manager.show_notification(notification_id, title, message, category)

    def dock_widget_to_character(self, widget_id: str, char_x: int, char_y: int, char_w: int, mode: str = "right"):
        self.controller.dock_widget_to_character(widget_id, char_x, char_y, char_w, mode)

    @property
    def widget_manager(self):
        return self.controller.widget_manager
