import os
import json
from PySide6.QtWidgets import QWidget
from desktop.platform.shared.interfaces.logging import ILoggingService

class WindowManager:
    """
    Abstracts UI rendering logic to preserve interaction context during Presence transitions.
    Maintains geometry, visibility, and state for the main expression window.
    """
    def __init__(self, logger: ILoggingService, state_path: str):
        self.logger = logger
        self.state_path = state_path
        self._window: QWidget = None
        self._state = {
            "geometry": None,
            "visibility": "hidden",
            "monitor": None
        }
        self.load_state()

    def set_window(self, window: QWidget):
        self._window = window
        self._restore_geometry()

    def show_expression(self):
        if self._window:
            self._window.show()
            self._window.activateWindow()
            self._window.raise_()
            self._state["visibility"] = "visible"
            self.save_state()

    def hide_expression(self):
        if self._window:
            self._save_geometry()
            self._window.hide()
            self._state["visibility"] = "hidden"
            self.save_state()

    def toggle_expression(self):
        if self._window and self._window.isVisible():
            self.hide_expression()
        else:
            self.show_expression()

    def _save_geometry(self):
        if self._window:
            rect = self._window.geometry()
            self._state["geometry"] = {
                "x": rect.x(),
                "y": rect.y(),
                "width": rect.width(),
                "height": rect.height()
            }

    def _restore_geometry(self):
        if self._window and self._state.get("geometry"):
            geo = self._state["geometry"]
            self._window.setGeometry(geo["x"], geo["y"], geo["width"], geo["height"])

    def load_state(self):
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r") as f:
                    self._state = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load window state: {e}")

    def save_state(self):
        self._save_geometry()
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, "w") as f:
                json.dump(self._state, f)
        except Exception as e:
            self.logger.error(f"Failed to save window state: {e}")
