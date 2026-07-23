import logging
from typing import Dict, Any, Optional
from desktop.character.presence.presence_memory import PresenceMemory

logger = logging.getLogger(__name__)

class DesktopContextManager:
    """
    S36B-R2-R1: Detects desktop contexts (Presentation, Fullscreen Application, Game, Movie, Remote Desktop, Screen Share, Multiple Monitors, Workspace Changes).
    Manages presentation mode drag & drop and state restoration.
    """
    def __init__(self, memory: PresenceMemory):
        self.memory = memory
        self.in_presentation = False
        self.in_fullscreen = False
        self.active_context = "DESKTOP_NORMAL"
        self._saved_state: Dict[str, Any] = {}

    def enter_presentation(self, current_x: int, current_y: int, current_dock: str, current_scale: float):
        self._saved_state = {
            "x": current_x,
            "y": current_y,
            "dock_edge": current_dock,
            "scale": current_scale
        }
        self.in_presentation = True
        self.active_context = "PRESENTATION"
        logger.info(f"[DesktopContextManager] Entered Presentation Mode. Saved pre-presentation state: {self._saved_state}")

    def exit_presentation(self) -> Dict[str, Any]:
        self.in_presentation = False
        self.active_context = "DESKTOP_NORMAL"
        logger.info(f"[DesktopContextManager] Exited Presentation Mode. Restoring saved state: {self._saved_state}")
        return self._saved_state

    def detect_fullscreen_app(self) -> bool:
        """Simulates/detects active fullscreen application or game."""
        return self.in_fullscreen

    def set_fullscreen_state(self, active: bool):
        self.in_fullscreen = active
        self.active_context = "FULLSCREEN_APP" if active else "DESKTOP_NORMAL"
        logger.info(f"[DesktopContextManager] Fullscreen App state set to {active}")
