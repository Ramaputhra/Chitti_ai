import logging
from typing import Optional, List, Dict, Any
from desktop.ui.widgets.runtime.widget_manager import WidgetManager
from desktop.ui.widgets.sdk.widget import BaseWidget
from desktop.ui.widgets.sdk.widget_session import WidgetSession
from desktop.ui.runtime.desktop_ui_runtime import DesktopUIRuntime

logger = logging.getLogger(__name__)

class WidgetRuntime:
    """
    S36D-2: Master Desktop Widget Framework Facade.
    STRICT CONSUMER of Desktop UI Runtime Foundation.
    Governs Widget Runtime, Widget SDK, Widget Registry, Widget Lifecycle, Widget Manifests, Session Binding,
    Generic Widgets, Preview Studio, and Widget Validation.
    Widgets visualize Runtime Sessions ONLY. Widgets SHALL NEVER execute Capabilities.
    """
    def __init__(self, ui_runtime: Optional[DesktopUIRuntime] = None):
        self.ui_runtime = ui_runtime or DesktopUIRuntime()
        self.widget_manager = WidgetManager(ui_runtime=self.ui_runtime)
        logger.info("[WidgetRuntime] Desktop Widget Framework initialized cleanly.")

    def start(self):
        self.ui_runtime.start()
        logger.info("[WidgetRuntime] Widget Runtime Started.")

    def stop(self):
        self.ui_runtime.stop()
        logger.info("[WidgetRuntime] Widget Runtime Stopped.")

    def create_widget(self, widget_id: str, widget_type: str, session: Optional[WidgetSession] = None) -> BaseWidget:
        return self.widget_manager.create_widget(widget_id, widget_type, session)

    def bind_session(self, widget_id: str, session: WidgetSession):
        self.widget_manager.bind_session(widget_id, session)

    def attach_widget_to_character(self, widget_id: str, anchor: dict, mode: str = "right"):
        self.widget_manager.attach_widget_to_character(widget_id, anchor, mode)

    def close_widget(self, widget_id: str):
        self.widget_manager.close_widget(widget_id)

    def hot_reload(self) -> bool:
        self.widget_manager.registry.manifest_loader.hot_reload()
        return self.ui_runtime.hot_reload()
