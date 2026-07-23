import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class HotkeyListener:
    """
    S36E: Listens for user-configurable global hotkeys (e.g. Ctrl+Space, Alt+C, Win+C).
    Restores CHITTI from System Tray or Presence Dot.
    """
    def __init__(self, shortcut: str = "Ctrl+Space"):
        self.shortcut = shortcut
        self.is_listening = False
        self._callback: Optional[Callable[[], None]] = None

    def configure_shortcut(self, new_shortcut: str):
        self.shortcut = new_shortcut
        logger.info(f"[HotkeyListener] Configured global hotkey: '{self.shortcut}'")

    def start_listening(self, callback: Callable[[], None]):
        self._callback = callback
        self.is_listening = True
        logger.info(f"[HotkeyListener] Hotkey Listener ACTIVE for '{self.shortcut}'")

    def stop_listening(self):
        self.is_listening = False
        logger.info(f"[HotkeyListener] Hotkey Listener STOPPED")

    def trigger_hotkey_press(self):
        """Simulates or handles global hotkey press."""
        if self.is_listening and self._callback:
            logger.info(f"[HotkeyListener] Hotkey '{self.shortcut}' triggered!")
            self._callback()
