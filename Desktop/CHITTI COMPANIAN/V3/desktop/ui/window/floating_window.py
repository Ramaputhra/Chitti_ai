from desktop.ui.window.transparent_window import TransparentWindow

class FloatingWindow(TransparentWindow):
    """S36D-1: Generic Desktop Floating Window."""
    def __init__(self, window_id: str, x: int = 100, y: int = 100, width: int = 320, height: int = 200):
        super().__init__(window_id, window_type="FloatingWindow", x=x, y=y, width=width, height=height)
