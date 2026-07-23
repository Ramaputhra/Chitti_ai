import sys
from typing import Optional
from PySide6.QtWidgets import QApplication
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.product.ui.expression_shell import ExpressionShell

class UIManager:
    """
    Manages all UI components for CHITTI.
    Ensures that temporary windows are spawned and destroyed correctly,
    while the ExpressionShell remains persistent.
    """
    def __init__(self, logger: ILoggingService, event_bus: IEventBus):
        self.logger = logger
        self.event_bus = event_bus
        
        # We ensure QApplication exists
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
            
        self.app.setQuitOnLastWindowClosed(False)
        self.shell: Optional[ExpressionShell] = None

    def initialize(self) -> None:
        self.logger.info("Initializing UIManager...")
        
        # Initialize Presence Runtime
        from desktop.runtimes.presence.activity_monitor import ActivityMonitor
        from desktop.runtimes.presence.monitor import MonitorManager
        from desktop.runtimes.presence.hotkeys.windows import WindowsHotkeyProvider
        from desktop.runtimes.presence.manager import PresenceManager

        self.activity_monitor = ActivityMonitor(self.logger, self.event_bus)
        self.activity_monitor.initialize()
        
        self.monitor_manager = MonitorManager()
        self.hotkey_provider = WindowsHotkeyProvider(self.logger)
        
        # Register global hotkey (example: Ctrl+Alt+Space)
        self.hotkey_provider.register_hotkey("ctrl+alt+space", lambda: self.activity_monitor.report_hotkey_activity("ctrl+alt+space"))
        
        self.presence_manager = PresenceManager(
            self.logger, self.event_bus, self.activity_monitor, self.monitor_manager
        )
        
        # Initialize Shell
        self.shell = ExpressionShell(self.logger, self.event_bus, self.activity_monitor, self.monitor_manager)
        self.shell.show()
        
        # Bind Shell to Presence Manager
        self.presence_manager.initialize(self.shell)

    def show_authentication_window(self, service_name: str) -> None:
        """
        Temporary Dialog support.
        The window is created, shown, and destroyed when done,
        leaving the ExpressionShell persistent.
        """
        self.logger.info(f"Opening authentication window for {service_name}")
        # Implementation would instantiate e.g. AuthenticationDialog and call .exec()
        pass

    def show_settings_window(self) -> None:
        self.logger.info("Opening Settings window")
        # Implementation would instantiate SettingsDialog and call .exec()
        pass

    def run(self) -> int:
        self.logger.info("Starting UI Event Loop...")
        return self.app.exec()

    def shutdown(self) -> None:
        self.logger.info("Shutting down UI Manager...")
        if self.shell:
            self.shell.close()
        self.app.quit()
