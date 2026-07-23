from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from desktop.ui.widgets.sdk.widget_session import WidgetSession
from desktop.ui.widgets.sdk.widget_context import WidgetContext
from desktop.ui.widgets.sdk.widget_theme import WidgetTheme
from desktop.ui.window.transparent_window import TransparentWindow

class BaseWidget(ABC):
    """
    S36D-2: Canonical Base Widget SDK class.
    Every widget MUST inherit from BaseWidget and implement the Widget Contract.
    Widgets SHALL visualize Runtime Sessions ONLY.
    Widgets SHALL NEVER create windows directly; they request windows from Desktop UI Runtime Foundation.
    Widgets SHALL NEVER execute Capabilities.
    """
    def __init__(self, widget_id: str, widget_type: str):
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.context = WidgetContext()
        self.window: Optional[TransparentWindow] = None
        self.expanded = False
        self.docked = False
        self.visible = False
        self.dock_edge: Optional[str] = None

    @abstractmethod
    def initialize(self, context: Optional[WidgetContext] = None):
        pass

    def bind_session(self, session: WidgetSession):
        self.context.session = session
        self.visible = session.active

    @abstractmethod
    def update(self, delta_data: Dict[str, Any]):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

    def expand(self):
        self.expanded = True

    def collapse(self):
        self.expanded = False

    def dock(self, edge: str = "right"):
        self.docked = True
        self.dock_edge = edge
        if self.window:
            self.window.dock(edge)

    def undock(self):
        self.docked = False
        self.dock_edge = None
        if self.window:
            self.window.undock()

    def attach(self, target_type: str, anchor_data: Dict[str, Any]):
        if self.window:
            self.window.attachment.attach(target_type, anchor_data)

    def detach(self):
        if self.window:
            self.window.attachment.detach()

    def show(self):
        self.visible = True
        if self.window:
            self.window.show()

    def hide(self):
        self.visible = False
        if self.window:
            self.window.hide()

    def close(self):
        self.visible = False
        if self.context.session:
            self.context.session.active = False
        if self.window:
            self.window.hide()

    def destroy(self):
        self.close()
        if self.window:
            self.window.destroy()
            self.window = None
        self.context.session = None
