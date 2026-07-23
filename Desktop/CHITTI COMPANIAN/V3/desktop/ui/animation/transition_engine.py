import logging
from desktop.ui.window.transparent_window import TransparentWindow

logger = logging.getLogger(__name__)

class TransitionEngine:
    """
    S36D-1: Window Entry/Exit Transition Engine.
    """
    def play_fade_in(self, window: TransparentWindow):
        window.opacity = 1.0
        logger.info(f"[TransitionEngine] Played Fade-In transition for window '{window.window_id}'.")

    def play_fade_out(self, window: TransparentWindow):
        window.opacity = 0.0
        logger.info(f"[TransitionEngine] Played Fade-Out transition for window '{window.window_id}'.")
