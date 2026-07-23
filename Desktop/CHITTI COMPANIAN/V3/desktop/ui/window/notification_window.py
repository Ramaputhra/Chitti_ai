from desktop.ui.window.transparent_window import TransparentWindow

class NotificationWindow(TransparentWindow):
    """S36D-1: Generic Desktop Notification Window."""
    def __init__(self, window_id: str, x: int = 1540, y: int = 40, width: int = 340, height: int = 120):
        super().__init__(window_id, window_type="NotificationWindow", x=x, y=y, width=width, height=height)
        self.auto_dismiss_ms = 5000
