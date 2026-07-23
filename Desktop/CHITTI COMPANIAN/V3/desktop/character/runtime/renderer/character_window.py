import logging
from typing import Optional
from desktop.character.runtime.runtime.runtime_state_machine import CharacterWindowState
from desktop.character.runtime.renderer.overlay_renderer import OverlayRenderer, DebugOverlayState

logger = logging.getLogger(__name__)

class CharacterWindow:
    """
    S36B: High-level Character Window Manager abstraction.
    Specifies transparent, always-on-top, click-through, movable, screen-edge docking,
    and debug overlay rendering capabilities.
    """
    def __init__(self, width: int = 400, height: int = 400):
        self.width = width
        self.height = height
        self.x = 100
        self.y = 100
        self.always_on_top = True
        self.click_through = False
        self.debug_mode = False
        self.overlay_renderer = OverlayRenderer()
        self.state = CharacterWindowState.HIDDEN

    def show(self):
        self.state = CharacterWindowState.VISIBLE
        logger.info("[CharacterWindow] Window VISIBLE")

    def hide(self):
        self.state = CharacterWindowState.HIDDEN
        logger.info("[CharacterWindow] Window HIDDEN")

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y

    def dock_to_edge(self, edge: str = "right"):
        if edge == "right":
            self.x = 1920 - self.width
            self.y = 1080 // 2 - self.height // 2
        elif edge == "left":
            self.x = 0
            self.y = 1080 // 2 - self.height // 2
        logger.info(f"[CharacterWindow] Docked to {edge} edge: ({self.x}, {self.y})")

    def render_debug_overlay(self, overlay_state: DebugOverlayState) -> str:
        if self.debug_mode:
            return self.overlay_renderer.format_debug_text(overlay_state)
        return ""
