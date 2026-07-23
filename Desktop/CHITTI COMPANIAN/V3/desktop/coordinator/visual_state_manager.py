from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CanonicalVisualState(Enum):
    SPEAKING = "Speaking"
    LISTENING = "Listening"
    THINKING = "Thinking"
    WORKING = "Working"
    PRESENTING = "Presenting"
    DOWNLOADING = "Downloading"
    PRINTING = "Printing"
    IDLE = "Idle"
    SLEEPING = "Sleeping"
    BUSY = "Busy"
    BACKGROUND = "Background"
    PRESENTATION = "Presentation"
    FULLSCREEN = "Fullscreen"

class VisualStateManager:
    """
    S36E: Visual State Manager exposing ONE canonical visual state for CHITTI.
    """
    def __init__(self, initial_state: CanonicalVisualState = CanonicalVisualState.IDLE):
        self._state = initial_state

    @property
    def current_state(self) -> CanonicalVisualState:
        return self._state

    def transition_to(self, target: CanonicalVisualState) -> bool:
        logger.info(f"[VisualStateManager] Canonical Visual State Transition: '{self._state.value}' -> '{target.value}'")
        self._state = target
        return True
