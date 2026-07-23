import logging
from typing import List, Dict
from desktop.ui.window.transparent_window import TransparentWindow

logger = logging.getLogger(__name__)

class ZOrderManager:
    """
    S36D-1: Manages Desktop Window Z-Ordering & Layer Stack.
    """
    def __init__(self):
        self._stack: List[str] = []

    def bring_to_front(self, window_id: str):
        if window_id in self._stack:
            self._stack.remove(window_id)
        self._stack.append(window_id)
        logger.info(f"[ZOrderManager] Window '{window_id}' brought to front.")

    def send_to_back(self, window_id: str):
        if window_id in self._stack:
            self._stack.remove(window_id)
        self._stack.insert(0, window_id)
        logger.info(f"[ZOrderManager] Window '{window_id}' sent to back.")

    def get_stack(self) -> List[str]:
        return list(self._stack)
