import logging
from typing import List, Tuple
from desktop.ui.window.transparent_window import TransparentWindow

logger = logging.getLogger(__name__)

class LayoutEngine:
    """
    S36D-1: Layout Engine supporting Single Window, Multiple Windows, Stack Layout, Auto Layout.
    """
    def apply_stack_layout(self, windows: List[TransparentWindow], start_x: int = 100, start_y: int = 100, offset_y: int = 20):
        current_y = start_y
        for win in windows:
            win.move(start_x, current_y)
            current_y += win.height + offset_y
        logger.info(f"[LayoutEngine] Applied Stack Layout to {len(windows)} windows.")
