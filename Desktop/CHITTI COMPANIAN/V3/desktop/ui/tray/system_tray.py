from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject

class SystemTray(QObject):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        
        self.tray_icon = QSystemTrayIcon(self)
        # Using a default Qt icon for MVP, typically we'd load 'assets/icons/chitti.png'
        self.tray_icon.setIcon(self.app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        self.menu = QMenu()
        
        self.action_start = QAction("Start CHITTI", self)
        self.action_settings = QAction("Settings", self)
        self.action_status = QAction("Status", self)
        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.app.quit)
        
        self.menu.addAction(self.action_start)
        self.menu.addAction(self.action_settings)
        self.menu.addAction(self.action_status)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
