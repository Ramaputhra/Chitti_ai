import logging
from typing import Optional, Dict, Any
from desktop.ui.runtime.runtime_controller import RuntimeController
from desktop.ui.window.transparent_window import TransparentWindow

logger = logging.getLogger(__name__)

class DesktopUIRuntime:
    """
    S36D-1: Master Desktop UI Runtime Foundation Facade.
    The canonical desktop rendering platform for CHITTI.
    Generic Desktop Operating Layer governing Windows, Overlays, Notifications, Floating Windows, Dialogs,
    Rendering Profiles, Motion Integration, Layout Engine, Asset Pipeline, and Theme System.
    PROHIBITED: Desktop UI Runtime SHALL NEVER render Character PNG assets or move Character Window directly.
    """
    def __init__(self):
        self.controller = RuntimeController()
        logger.info("[DesktopUIRuntime] Desktop UI Runtime Foundation initialized cleanly.")

    def start(self):
        self.controller.start()

    def stop(self):
        self.controller.stop()

    def create_window(self, window_id: str, window_type: str = "FloatingWindow", x: int = 100, y: int = 100, width: int = 360, height: int = 240) -> TransparentWindow:
        return self.controller.window_manager.create_window(window_id, window_type, x=x, y=y, width=width, height=height)

    def destroy_window(self, window_id: str):
        self.controller.window_manager.destroy_window(window_id)

    def attach_window_to_character(self, window_id: str, anchor: Dict[str, int], mode: str = "right"):
        win = self.controller.window_manager.get_window(window_id)
        if win:
            nx, ny = self.controller.docking_engine.calculate_character_attached_position(anchor, win.width, win.height, mode)
            win.move(nx, ny)
            win.dock(mode)
            win.attachment.attach("CHARACTER_ANCHOR", anchor)

    def render_frame(self, window_id: str, profile: str = "WIDGET") -> str:
        return self.controller.renderer.render_window_frame(window_id, profile=profile)

    def set_theme(self, name: str) -> bool:
        return self.controller.theme_manager.set_theme(name)

    def hot_reload(self) -> bool:
        a_ok = self.controller.asset_loader.hot_reload_assets()
        self.controller.renderer.asset_cache.reload()
        return a_ok
