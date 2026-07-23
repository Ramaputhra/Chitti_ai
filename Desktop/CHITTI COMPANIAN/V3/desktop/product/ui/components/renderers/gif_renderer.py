import os
from typing import Any, Dict
from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout

from .base_renderer import BaseRenderer

class GifRenderer(QWidget, BaseRenderer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_state = "idle"
        self._cache: Dict[str, QMovie] = {}
        self._loop_config: Dict[str, bool] = {}
        
        # UI Setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def preload(self, profile: Dict[str, Any]) -> None:
        """
        Expects profile dictionary loaded from yaml:
        {
          "states": {
            "idle": {"asset": "idle.gif", "loop": true, ...},
            ...
          }
        }
        """
        profile_dir = profile.get("_base_dir", "")
        states = profile.get("states", {})
        
        for state_name, config in states.items():
            asset_filename = config.get("asset", "")
            if not asset_filename:
                continue
                
            full_path = os.path.join(profile_dir, asset_filename)
            if os.path.exists(full_path):
                movie = QMovie(full_path)
                # Decode first frame into memory
                movie.jumpToFrame(0)
                self._cache[state_name] = movie
                self._loop_config[state_name] = config.get("loop", True)

    def play(self, state: str) -> None:
        if state not in self._cache:
            # Fallback to idle if missing
            state = "idle"
            
        if state not in self._cache:
            return # Even idle is missing
            
        if self._current_state != state and self._current_state in self._cache:
            old_movie = self._cache[self._current_state]
            old_movie.stop()
            
        self._current_state = state
        movie = self._cache[state]
        self.label.setMovie(movie)
        
        if not self._loop_config.get(state, True):
            # If not looping, we'd theoretically connect the finished signal
            # For phase 1, QMovie loops by default unless configured differently.
            pass
            
        movie.start()

    def stop(self) -> None:
        if self._current_state in self._cache:
            self._cache[self._current_state].stop()

    def pause(self) -> None:
        if self._current_state in self._cache:
            self._cache[self._current_state].setPaused(True)

    def resume(self) -> None:
        if self._current_state in self._cache:
            self._cache[self._current_state].setPaused(False)

    def current_state(self) -> str:
        return self._current_state
