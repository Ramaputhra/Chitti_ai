import logging
from desktop.ui.presence.presence_state import PresenceState, PresenceStateChanged

logger = logging.getLogger(__name__)

class AudioPlayer:
    """
    Mock Audio Player that syncs sound effects with PresenceState changes.
    Subscribes directly to PresenceStateChanged events from the EventBus (Rule 34).
    """
    def __init__(self, event_bus=None):
        if event_bus and hasattr(event_bus, "subscribe"):
            event_bus.subscribe("Presence.StateChanged", self._handle_presence_state_changed)
            
        # Map states to specific audio files
        self.state_sounds = {
            PresenceState.SUCCESS: "success_chime.wav",
            PresenceState.FAILURE: "error_buzz.wav",
            PresenceState.LISTENING: "listening_blip.wav",
            PresenceState.UNDERSTANDING: "processing.wav",
            PresenceState.WORKING: "task_started.wav",
            PresenceState.ERROR: "error_buzz.wav"
        }

    def _handle_presence_state_changed(self, event: PresenceStateChanged):
        """Reacts to state changes published by PresenceEngine."""
        self.play_state(event.current)

    def play_state(self, state: PresenceState):
        # Note: If TTS is running (TALKING state), we do NOT play a sound effect 
        # here because the TTS engine is already playing the audio.
        if state == PresenceState.TALKING:
            return

        sound_file = self.state_sounds.get(state)
        if sound_file:
            self._play_sound(sound_file)

    def play_event(self, event_name: str):
        # Example for one-shot events like "Yeah" or "Celebrate"
        logger.info(f"[Mock Audio] Playing event sound effect for: {event_name}")

    def stop(self):
        logger.info("[Mock Audio] Stopping all audio.")

    def _play_sound(self, file_name: str):
        # TODO: Implement actual audio playback here
        logger.info(f"[Mock Audio] Playing sound effect: {file_name}")
