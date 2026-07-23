from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.models.lifecycle import ShutdownRequest, ShutdownReason
from desktop.runtimes.presence.models import RuntimeMode

class SystemTrayService(QObject):
    """
    Manages the system tray icon and context menu.
    Publishes events to the EventBus instead of managing lifecycle directly.
    """
    def __init__(self, event_bus: IEventBus, icon_path: str):
        super().__init__()
        self.event_bus = event_bus
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_path))
        
        self.menu = QMenu()
        
        # Menu Actions
        self.restore_action = QAction("Restore", self)
        self.restore_action.triggered.connect(self._on_restore)
        self.menu.addAction(self.restore_action)
        
        self.status_action = QAction("Status", self)
        self.status_action.triggered.connect(self._on_status)
        self.menu.addAction(self.status_action)
        
        self.history_action = QAction("Conversation History", self)
        self.history_action.triggered.connect(self._on_history)
        self.menu.addAction(self.history_action)
        
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self._on_settings)
        self.menu.addAction(self.settings_action)
        
        self.dev_console_action = QAction("Developer Console", self)
        self.dev_console_action.triggered.connect(self._on_dev_console)
        self.menu.addAction(self.dev_console_action)
        
        self.menu.addSeparator()
        
        self.quiet_action = QAction("Pause Listening (Quiet Mode)", self)
        self.quiet_action.triggered.connect(self._on_quiet_mode)
        self.menu.addAction(self.quiet_action)
        
        self.sleep_action = QAction("Sleep", self)
        self.sleep_action.triggered.connect(self._on_sleep_mode)
        self.menu.addAction(self.sleep_action)
        
        self.menu.addSeparator()
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self._on_quit)
        self.menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # Listen for tray removal event
        self.event_bus.subscribe("Lifecycle.RemoveTray", self._on_remove_tray)
        
    def show(self):
        self.tray_icon.show()
        
    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self._on_restore()
            
    def _on_restore(self):
        self.event_bus.publish(Event("UI.RestoreRequest", None))
        
    def _on_status(self):
        self.event_bus.publish(Event("UI.StatusRequest", None))
        
    def _on_history(self):
        self.event_bus.publish(Event("UI.HistoryRequest", None))
        
    def _on_settings(self):
        self.event_bus.publish(Event("UI.SettingsRequest", None))
        
    def _on_dev_console(self):
        self.event_bus.publish(Event("UI.DevConsoleRequest", None))
        
    def _on_quiet_mode(self):
        self.event_bus.publish(Event("Presence.RuntimeModeChanged", {"mode": RuntimeMode.QUIET}))
        
    def _on_sleep_mode(self):
        self.event_bus.publish(Event("Presence.RuntimeModeChanged", {"mode": RuntimeMode.SLEEP}))
        
    def _on_quit(self):
        request = ShutdownRequest(reason=ShutdownReason.USER, message="User triggered quit from tray.")
        self.event_bus.publish(Event("System.ShutdownRequest", request))
        
    def _on_remove_tray(self, event: Event):
        self.tray_icon.hide()
