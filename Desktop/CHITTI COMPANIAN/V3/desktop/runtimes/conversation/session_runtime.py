import logging
import time
import threading
import uuid
from typing import Any, Optional

from desktop.platform.shared.interfaces.event_bus import Event
from desktop.models.conversation_models import (
    SessionState,
    ConversationSessionStartedEvent,
    ConversationSessionEndedEvent,
    ConversationTurnStartedEvent,
    ConversationTurnCompletedEvent
)
from desktop.platform.core.session_context import SessionContext

logger = logging.getLogger(__name__)

class ConversationSessionRuntime:
    """
    Manages the overarching conversation session (Rule 104).
    Keeps track of SessionState and triggers WAITING_FOR_REPLY / auto-resume.
    """
    def __init__(self, event_bus: Any, session_context: SessionContext, timeout_sec: float = 30.0):
        self.event_bus = event_bus
        self.context = session_context
        self.timeout_sec = timeout_sec
        self.state = SessionState.IDLE
        
        self._timer: Optional[threading.Timer] = None
        
        if hasattr(self.event_bus, "subscribe"):
            # Triggers for starting a session / turn
            self.event_bus.subscribe("WAKE_WORD_DETECTED", self._on_wake_word)
            self.event_bus.subscribe("USER_TRANSCRIPT_GENERATED", self._on_transcript)
            
            # Capability execution context tracking
            self.event_bus.subscribe("CapabilityExecuted", self._on_capability_executed)
            
            # Triggers for ending a turn
            self.event_bus.subscribe("Voice.PlaybackCompleted", self._on_tts_finished)
            
    def start(self):
        logger.info("ConversationSessionRuntime started.")
        
    def _transition(self, new_state: SessionState):
        logger.info(f"ConversationSession state: {self.state.name} -> {new_state.name}")
        self.state = new_state
        
        if self._timer:
            self._timer.cancel()
            self._timer = None
            
        if self.state == SessionState.WAITING_FOR_REPLY:
            # Start timeout
            self._timer = threading.Timer(self.timeout_sec, self._on_timeout)
            self._timer.start()
            
            # Instruct UI/Avatar that we are listening again
            self.event_bus.publish(Event("SPEECH_STATE_CHANGED", source="SessionRuntime", payload={"state": "LISTENING"}))
            
    def _on_timeout(self):
        logger.info("ConversationSession timeout reached. Ending session.")
        self._end_session("timeout")
        
    def _start_session_if_idle(self):
        if self.state == SessionState.IDLE:
            self.context.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            logger.info(f"Starting new conversation session: {self.context.conversation_id}")
            self.event_bus.publish(Event(
                "ConversationSessionStarted", 
                source="SessionRuntime",
                payload={"event": ConversationSessionStartedEvent(
                    conversation_id=self.context.conversation_id,
                    timestamp=time.time()
                )}
            ))
            self._transition(SessionState.ACTIVE_SESSION)
            
    def _end_session(self, reason: str):
        if self.state != SessionState.IDLE:
            self.event_bus.publish(Event(
                "ConversationSessionEnded",
                source="SessionRuntime",
                payload={"event": ConversationSessionEndedEvent(
                    conversation_id=self.context.conversation_id,
                    reason=reason,
                    timestamp=time.time()
                )}
            ))
            self.context.current_turn_id = None
            self._transition(SessionState.IDLE)
            
            # Let other runtimes know we are asleep
            self.event_bus.publish(Event("SPEECH_STATE_CHANGED", source="SessionRuntime", payload={"state": "SLEEPING"}))

    def _on_wake_word(self, event_data: Any):
        self._start_session_if_idle()
        if self.state == SessionState.WAITING_FOR_REPLY:
            self._transition(SessionState.ACTIVE_SESSION)
            
    def _on_transcript(self, event_data: Any):
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        text = payload.get("text", "")
        if not text:
            return
            
        self._start_session_if_idle()
        self._transition(SessionState.ACTIVE_SESSION)
        
        # Start a new turn
        self.context.current_turn_id = f"turn_{uuid.uuid4().hex[:8]}"
        
        self.event_bus.publish(Event(
            "ConversationTurnStarted",
            source="SessionRuntime",
            payload={"event": ConversationTurnStartedEvent(
                conversation_id=self.context.conversation_id,
                turn_id=self.context.current_turn_id,
                source="voice", # Could be passed in payload
                user_input=text,
                timestamp=time.time()
            )}
        ))
        
    def _on_capability_executed(self, event_data: Any):
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        tool = payload.get("tool")
        if tool:
            self.context.update_from_execution(tool, payload.get("metadata", {}))
            
    def _on_tts_finished(self, event_data: Any):
        # A turn is completed when CHITTI finishes speaking
        if self.state == SessionState.ACTIVE_SESSION:
            self.event_bus.publish(Event(
                "ConversationTurnCompleted",
                source="SessionRuntime",
                payload={"event": ConversationTurnCompletedEvent(
                    conversation_id=self.context.conversation_id,
                    turn_id=self.context.current_turn_id or "unknown",
                    response_text="[Audio Response Played]",
                    capabilities_executed=[self.context.previous_capability] if self.context.previous_capability else [],
                    timestamp=time.time()
                )}
            ))
            
            # Go into WAITING_FOR_REPLY (Auto-resume listening)
            self._transition(SessionState.WAITING_FOR_REPLY)
