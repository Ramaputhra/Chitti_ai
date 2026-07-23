import logging
from desktop.runtimes.expression.events import ExpressionStarted

logger = logging.getLogger(__name__)

class AudioRuntime:
    """
    Interprets declarative audio asset symbolic names into physical sound.
    (Rule 37: Output Independence)
    """
    def __init__(self, event_bus=None):
        if event_bus and hasattr(event_bus, "subscribe"):
            event_bus.subscribe("Expression.Started", self._handle_expression_started)
            
    def _handle_expression_started(self, event: ExpressionStarted):
        """Reacts to a coordinated expression request."""
        audio_config = event.outputs.get("audio", {})
        sound_id = audio_config.get("sound")
        
        if sound_id:
            self._play_sound(sound_id)
        else:
            self.stop()

    def stop(self):
        # logger.debug("[Mock Audio] Stopping all audio.")
        pass

    def _play_sound(self, sound_id: str):
        # TODO: Implement actual audio playback here (e.g. pygame.mixer.Sound(sound_id).play())
        logger.info(f"[Audio Runtime] Playing sound effect: {sound_id}")
