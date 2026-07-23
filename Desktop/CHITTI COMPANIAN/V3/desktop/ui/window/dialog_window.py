from desktop.ui.window.transparent_window import TransparentWindow

class DialogWindow(TransparentWindow):
    """S36D-1: Generic Desktop Dialog Window."""
    def __init__(self, window_id: str, x: int = 400, y: int = 300, width: int = 480, height: int = 300):
        super().__init__(window_id, window_type="DialogWindow", x=x, y=y, width=width, height=height)
        self.modal = True
