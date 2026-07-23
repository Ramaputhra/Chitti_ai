import logging
from typing import Dict, Optional, List
from desktop.ui.window.transparent_window import TransparentWindow
from desktop.ui.window.overlay_window import OverlayWindow
from desktop.ui.window.floating_window import FloatingWindow
from desktop.ui.window.dialog_window import DialogWindow
from desktop.ui.window.notification_window import NotificationWindow
from desktop.ui.window.window_layers import SemanticWindowLayer, WindowLayerTranslator
from desktop.ui.window.window_registry import WindowRegistry
from desktop.ui.window.z_order_manager import ZOrderManager

logger = logging.getLogger(__name__)

class WindowManager:
    """
    S36D-1-R1: Master Window Manager creating, positioning, and translating Semantic Window Layers into OS-specific ordering.
    """
    def __init__(self):
        self.registry = WindowRegistry()
        self.z_order_manager = ZOrderManager()

    def create_window(self, window_id: str, window_type: str = "FloatingWindow", x: int = 100, y: int = 100, width: int = 360, height: int = 240) -> TransparentWindow:
        layer_map = {
            "OverlayWindow": SemanticWindowLayer.SYSTEM_OVERLAY,
            "DialogWindow": SemanticWindowLayer.DIALOG,
            "NotificationWindow": SemanticWindowLayer.NOTIFICATION,
            "CharacterWidget": SemanticWindowLayer.CHARACTER_WIDGET,
            "FloatingWindow": SemanticWindowLayer.FLOATING_WIDGET,
            "DebugWindow": SemanticWindowLayer.DEBUG
        }
        layer = layer_map.get(window_type, SemanticWindowLayer.FLOATING_WIDGET)

        if window_type == "OverlayWindow":
            win = OverlayWindow(window_id, x=x, y=y, width=width, height=height)
        elif window_type == "DialogWindow":
            win = DialogWindow(window_id, x=x, y=y, width=width, height=height)
        elif window_type == "NotificationWindow":
            win = NotificationWindow(window_id, x=x, y=y, width=width, height=height)
        else:
            win = FloatingWindow(window_id, x=x, y=y, width=width, height=height)

        win.layer = layer
        self.registry.register(win)
        self.z_order_manager.bring_to_front(window_id)
        return win

    def destroy_window(self, window_id: str):
        win = self.registry.get(window_id)
        if win:
            win.destroy()
            self.registry.unregister(window_id)

    def get_window(self, window_id: str) -> Optional[TransparentWindow]:
        return self.registry.get(window_id)

    def verify_layer_ordering(self, win_lower: TransparentWindow, win_higher: TransparentWindow) -> bool:
        return WindowLayerTranslator.is_layer_above(win_higher.layer, win_lower.layer)
