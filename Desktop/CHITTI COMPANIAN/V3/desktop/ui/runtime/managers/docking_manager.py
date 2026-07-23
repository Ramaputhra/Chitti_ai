import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class DockingManager:
    """
    S36D: Docking Manager supporting Screen Edge Docking and Character-Attached Docking.
    Supports: Dock Right Of Character, Dock Left Of Character, Dock Below Character, Floating Beside Character.
    """
    def dock_to_character(self, widget_x: int, widget_y: int, char_x: int, char_y: int, char_w: int, mode: str = "right") -> Tuple[int, int]:
        if mode == "right":
            nx = char_x + char_w + 10
            ny = char_y
        elif mode == "left":
            nx = max(0, char_x - 300 - 10)
            ny = char_y
        elif mode == "below":
            nx = char_x
            ny = char_y + 400 + 10
        else:  # floating
            nx = char_x + char_w + 20
            ny = char_y + 20

        logger.info(f"[DockingManager] Docked widget to Character ({mode}): ({nx}, {ny})")
        return nx, ny
