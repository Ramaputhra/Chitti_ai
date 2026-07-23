import logging
from typing import Dict, Optional, List
from desktop.ui.widgets.sdk.widget import BaseWidget
from desktop.ui.widgets.generic_widget import GenericWidgetImpl
from desktop.ui.widgets.sdk.widget_session import WidgetSession
from desktop.ui.widgets.runtime.widget_registry import WidgetRegistry
from desktop.ui.widgets.runtime.widget_metrics import WidgetMetrics
from desktop.ui.widgets.runtime.widget_validator import WidgetValidator
from desktop.ui.runtime.desktop_ui_runtime import DesktopUIRuntime

logger = logging.getLogger(__name__)

class WidgetManager:
    """
    S36D-2: Widget Manager orchestrating lazy instantiation, session binding, and requesting windows
    from Desktop UI Runtime Foundation.
    Widgets SHALL visualize Runtime Sessions ONLY.
    Widgets SHALL NEVER execute Capabilities.
    """
    def __init__(self, ui_runtime: Optional[DesktopUIRuntime] = None):
        self.ui_runtime = ui_runtime or DesktopUIRuntime()
        self.registry = WidgetRegistry()
        self.metrics = WidgetMetrics()
        self.validator = WidgetValidator()

    def create_widget(self, widget_id: str, widget_type: str, session: Optional[WidgetSession] = None) -> BaseWidget:
        # Lazy instantiation
        widget = GenericWidgetImpl(widget_id=widget_id, widget_type=widget_type)
        widget.initialize()
        
        # Request generic window from Desktop UI Runtime Foundation
        win = self.ui_runtime.create_window(
            window_id=f"win_{widget_id}",
            window_type="CharacterWidget" if widget_type in ["Media", "Reminder", "Alarm"] else "FloatingWindow",
            x=200, y=200, width=360, height=240
        )
        widget.window = win

        if session:
            widget.bind_session(session)

        self.registry.register_widget(widget)
        self.metrics.record_widget_created()
        logger.info(f"[WidgetManager] Created widget '{widget_id}' ({widget_type}) requested window 'win_{widget_id}' from Desktop UI Runtime.")
        return widget

    def bind_session(self, widget_id: str, session: WidgetSession):
        w = self.registry.get_widget(widget_id)
        if w:
            w.bind_session(session)
            logger.info(f"[WidgetManager] Widget '{widget_id}' bound to session '{session.session_id}' ({session.session_type})")

    def attach_widget_to_character(self, widget_id: str, anchor: dict, mode: str = "right"):
        w = self.registry.get_widget(widget_id)
        if w and w.window:
            self.ui_runtime.attach_window_to_character(w.window.window_id, anchor, mode=mode)
            w.dock(mode)
            w.attach("CHARACTER_ANCHOR", anchor)

    def close_widget(self, widget_id: str):
        w = self.registry.get_widget(widget_id)
        if w:
            w.destroy()
            self.registry.unregister_widget(widget_id)
            self.metrics.record_widget_destroyed()
            logger.info(f"[WidgetManager] Closed widget '{widget_id}'")
