import logging
from typing import Optional, Dict, Any, List
from desktop.ui.runtime.managers.widget_manager import WidgetManager
from desktop.ui.runtime.managers.notification_manager import NotificationManager
from desktop.ui.runtime.managers.docking_manager import DockingManager
from desktop.ui.runtime.runtime.runtime_state_machine import DesktopUIRuntimeStateMachine, UIWindowState
from desktop.ui.runtime.widgets.base_widget import BaseWidget, UISession

logger = logging.getLogger(__name__)

class RuntimeController:
    """
    S36D: Runtime Controller orchestrating Widget Manager, Notification Manager, Docking Manager,
    and UI Window State Machine.
    """
    def __init__(self):
        self.widget_manager = WidgetManager()
        self.notification_manager = NotificationManager()
        self.docking_manager = DockingManager()
        self.state_machine = DesktopUIRuntimeStateMachine()
        self.is_running = False

    def start(self):
        self.is_running = True
        self.state_machine.transition_to(UIWindowState.VISIBLE)
        logger.info("[RuntimeController] Desktop UI Runtime Started.")

    def stop(self):
        self.is_running = False
        self.state_machine.transition_to(UIWindowState.HIDDEN)
        logger.info("[RuntimeController] Desktop UI Runtime Stopped.")

    def create_and_bind_widget(self, widget_id: str, widget_type: str, session: UISession) -> BaseWidget:
        widget = self.widget_manager.create_widget(widget_id, widget_type)
        self.widget_manager.bind_session(widget_id, session)
        return widget

    def dock_widget_to_character(self, widget_id: str, char_x: int, char_y: int, char_w: int, mode: str = "right"):
        w = self.widget_manager.get_widget(widget_id)
        if w:
            nx, ny = self.docking_manager.dock_to_character(w.x, w.y, char_x, char_y, char_w, mode)
            w.x = nx
            w.y = ny
            w.dock(mode)
