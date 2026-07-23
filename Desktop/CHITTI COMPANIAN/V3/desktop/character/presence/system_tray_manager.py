import logging

logger = logging.getLogger(__name__)

class SystemTrayManager:
    """
    S36E: System Tray Manager.
    In System Tray mode: Character Window & Presence Dot are Hidden; Background Runtime, Wake Engine,
    Hotkey Listener, Capability Runtime, and Background Tasks remain fully RUNNING.
    """
    def __init__(self):
        self.tray_active = True
        logger.info("[SystemTrayManager] System Tray Manager initialized cleanly.")

    def enter_system_tray(self):
        self.tray_active = True
        logger.info("[SystemTrayManager] Entered System Tray mode. Background tasks continue normally.")

    def exit_system_tray(self):
        logger.info("[SystemTrayManager] Exited System Tray mode.")
