import logging
from typing import Dict, Optional, List
from desktop.ui.window.transparent_window import TransparentWindow

logger = logging.getLogger(__name__)

class WindowRegistry:
    """
    S36D-1: Central Registry for active TransparentWindow instances.
    """
    def __init__(self):
        self._windows: Dict[str, TransparentWindow] = {}

    def register(self, window: TransparentWindow):
        self._windows[window.window_id] = window
        logger.info(f"[WindowRegistry] Registered window '{window.window_id}' ({window.window_type}).")

    def unregister(self, window_id: str):
        if window_id in self._windows:
            del self._windows[window_id]
            logger.info(f"[WindowRegistry] Unregistered window '{window_id}'.")

    def get(self, window_id: str) -> Optional[TransparentWindow]:
        return self._windows.get(window_id)

    def get_all(self) -> List[TransparentWindow]:
        return list(self._windows.values())
