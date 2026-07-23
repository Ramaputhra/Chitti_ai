import os
import yaml
from typing import Optional
from PySide6.QtCore import QObject, QTimer, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout

from desktop.platform.shared.interfaces.logging import ILoggingService
from .renderers.gif_renderer import GifRenderer
from .renderers.base_renderer import BaseRenderer

class AvatarRenderer(QWidget):
    """
    Manages Avatar profiles, transition queues, and commands the underlying renderer backend.
    """
    def __init__(self, logger: ILoggingService, parent=None):
        super().__init__(parent)
        self.logger = logger
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Instantiate backend (Phase 1: GIF)
        self.backend: BaseRenderer = GifRenderer(self)
        self.layout.addWidget(self.backend)
        
        self.profile = {}
        self._transition_queue = []
        self._is_in_min_duration = False
        self._min_duration_timer = QTimer(self)
        self._min_duration_timer.setSingleShot(True)
        self._min_duration_timer.timeout.connect(self._on_min_duration_elapsed)
        
    def load_profile(self, profile_path: str):
        """Loads avatar configuration and assets."""
        if not os.path.exists(profile_path):
            self.logger.error(f"Avatar profile not found: {profile_path}")
            return
            
        try:
            with open(profile_path, 'r') as f:
                self.profile = yaml.safe_load(f)
                
            # Add base directory for relative asset resolution
            self.profile["_base_dir"] = os.path.dirname(profile_path)
            
            self.backend.preload(self.profile)
            self.logger.info(f"Loaded avatar profile: {self.profile.get('name', 'unknown')}")
            
            # Start in idle state
            self.request_state("idle")
            
        except Exception as e:
            self.logger.error(f"Failed to load avatar profile: {e}")

    def request_state(self, state_name: str):
        """Requests a visual state change, respecting minimum duration locks."""
        # Enforce valid state
        states = self.profile.get("states", {})
        if state_name not in states and state_name != "idle":
            self.logger.warning(f"Unknown avatar state requested: {state_name}")
            return
            
        if self._is_in_min_duration:
            # Queue it up instead of interrupting immediately
            self._transition_queue.append(state_name)
            self.logger.debug(f"Queued state transition: {state_name}")
            return
            
        self._execute_state(state_name)

    def _execute_state(self, state_name: str):
        self.backend.play(state_name)
        
        # Lock transitions for minimum duration
        states = self.profile.get("states", {})
        config = states.get(state_name, {})
        min_duration = config.get("minimum_duration_ms", 0)
        
        if min_duration > 0:
            self._is_in_min_duration = True
            self._min_duration_timer.start(min_duration)
            
    @Slot()
    def _on_min_duration_elapsed(self):
        self._is_in_min_duration = False
        
        # If queue has items, jump to the MOST RECENT requested state (drop intermediate states to catch up)
        if self._transition_queue:
            next_state = self._transition_queue[-1]
            self._transition_queue.clear()
            self._execute_state(next_state)
