from desktop.ui.window.transparent_window import TransparentWindow

class OverlayWindow(TransparentWindow):
    """S36D-1: Generic Desktop Overlay Window."""
    def __init__(self, window_id: str, x: int = 0, y: int = 0, width: int = 1920, height: int = 1080):
        super().__init__(window_id, window_type="OverlayWindow", x=x, y=y, width=width, height=height)
        self.click_through = True
