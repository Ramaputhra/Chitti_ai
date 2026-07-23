import logging
import threading
from typing import Any, Dict, Optional

from desktop.models.audio_models import SpeechState, AudioSession
from desktop.platform.shared.interfaces.event_bus import Event

logger = logging.getLogger(__name__)

class SpeechOrchestrator:
    """
    Manages the continuous conversation loop with AudioSessions and Echo Protection.
    """
    def __init__(self, event_bus: Any, config: Dict[str, Any] = None):
        self.event_bus = event_bus
        self.state = SpeechState.SLEEPING
        self.current_session: Optional[AudioSession] = None
        self._echo_suspend = False
        
        # Subscriptions
        self.event_bus.subscribe("WAKE_WORD_DETECTED", self.on_wake_word)
        self.event_bus.subscribe("SPEECH_STARTED", self.on_speech_started)
        self.event_bus.subscribe("SPEECH_STOPPED", self.on_speech_stopped)
        self.event_bus.subscribe("TTS_STARTED", self.on_tts_started)
        self.event_bus.subscribe("TTS_FINISHED", self.on_tts_finished)
        self.event_bus.subscribe("USER_TRANSCRIPT_GENERATED", self.on_transcript_generated)
        self.event_bus.subscribe("SPEECH_STATE_CHANGED", self.on_external_state_changed)

    def transition(self, new_state: SpeechState) -> None:
        logger.info(f"SpeechOrchestrator transitioning: {self.state.name} -> {new_state.name}")
        self.state = new_state
        self.event_bus.publish(Event("SPEECH_STATE_CHANGED", source="SpeechOrchestrator", payload={"state": new_state.name}))
        
        if new_state == SpeechState.SLEEPING:
            if self.current_session:
                self.current_session.is_active = False
                self.current_session = None

    def on_wake_word(self, event: Dict[str, Any]) -> None:
        if self._echo_suspend:
            return
            
        if self.state == SpeechState.SLEEPING:
            payload = getattr(event, "payload", event.get("payload", {}) if isinstance(event, dict) else {})
            self.current_session = AudioSession(wake_source=payload.get("model", "unknown"))
            self.transition(SpeechState.WAKE_DETECTED)
            # Instantly move to LISTENING to capture follow-up speech
            self.transition(SpeechState.LISTENING)

    def on_speech_started(self, event: Dict[str, Any]) -> None:
        if self._echo_suspend:
            return
            
        if self.state == SpeechState.EXPECTING_REPLY:
            self.transition(SpeechState.LISTENING)

    def on_speech_stopped(self, event: Dict[str, Any]) -> None:
        if self._echo_suspend:
            return
            
        if self.state == SpeechState.LISTENING and self.current_session:
            self.transition(SpeechState.UNDERSTANDING)
            payload = getattr(event, "payload", event.get("payload", {}) if isinstance(event, dict) else {})
            buffer = payload.get("buffer", b"")
            self.current_session.speech_segments = bytearray(buffer)
            
            logger.info("Speech segment completed. Forwarding to STT.")
            self.event_bus.publish(Event("TRANSCRIBE_BUFFER", source="SpeechOrchestrator", payload={
                "session_id": self.current_session.id,
                "buffer": buffer
            }))

    def on_transcript_generated(self, event: Dict[str, Any]) -> None:
        payload = getattr(event, "payload", event.get("payload", {}) if isinstance(event, dict) else {})
        if self.current_session and payload.get("session_id") == self.current_session.id:
            text = payload.get("text", "").strip()
            self.current_session.transcript = text
            self.current_session.language = payload.get("language")
            
            if not text:
                logger.info("Transcript was empty. Returning to SLEEPING state.")
                self.transition(SpeechState.SLEEPING)
            else:
                self.transition(SpeechState.THINKING)
                # Session is fully assembled, Inference Runtime takes over from here
                pass

    def on_tts_started(self, event: Dict[str, Any]) -> None:
        """Echo Protection: Suspend all listening"""
        logger.debug("Echo Protection ACTIVE")
        self._echo_suspend = True

    def on_tts_finished(self, event: Dict[str, Any]) -> None:
        """Echo Protection: Resume listening"""
        logger.debug("Echo Protection DEACTIVATED")
        self._echo_suspend = False

    def on_external_state_changed(self, event: Any) -> None:
        source = getattr(event, "source", "")
        if source == "SpeechOrchestrator":
            return
            
        payload = getattr(event, "payload", event.get("payload", {}) if isinstance(event, dict) else {})
        state_str = payload.get("state")
        
        if state_str == "LISTENING":
            self.state = SpeechState.LISTENING
            if not self.current_session:
                self.current_session = AudioSession(wake_source="auto-resume")
        elif state_str == "SLEEPING":
            self.state = SpeechState.SLEEPING
            if self.current_session:
                self.current_session.is_active = False
                self.current_session = None
