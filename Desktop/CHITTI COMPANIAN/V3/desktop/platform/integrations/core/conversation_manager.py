import time
from typing import Any, Dict, Optional

from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.conversation_manager import IConversationManager
from desktop.platform.shared.interfaces.session_recorder import ISessionRecorder
from desktop.platform.shared.models.audio_state import AudioState
from desktop.platform.shared.models.session import ConversationSession


class ConversationManager(IConversationManager):
    def __init__(
        self, event_bus: IEventBus, logger: ILoggingService, recorder: ISessionRecorder
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.recorder = recorder
        self._state = ServiceState.STOPPED
        self._current_session: Optional[ConversationSession] = None

    @property
    def name(self) -> str:
        return "ConversationManager"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.event_bus.subscribe("Voice.WakeDetected", self._on_wake)
        self.event_bus.subscribe("Language.TextRecognized", self._on_text)
        self.event_bus.subscribe("Intent.Detected", self._on_intent)
        self.event_bus.subscribe("Response.Generated", self._on_response)
        self.event_bus.subscribe("System.Interrupt", self._on_interrupt)
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"has_active_session": self._current_session is not None}

    def get_current_session(self) -> Optional[ConversationSession]:
        return self._current_session

    def _on_wake(self, event: Event) -> None:
        if self._current_session:
            self.logger.warning("Double wake detected. Ignoring second wake.")
            return

        self._current_session = ConversationSession(
            trigger="Voice",
            wake_word=event.payload.get("wake_word", "unknown"),
            state=AudioState.WAKE_DETECTED,
        )
        self._current_session.latency.wake_detection_ms = 15.0  # Mock measurement

        self.logger.info(f"Conversation Started: {self._current_session.session_id}")
        self.event_bus.publish(
            Event(
                "Session.Started",
                self.name,
                {"session_id": self._current_session.session_id},
            )
        )

    def _on_text(self, event: Event) -> None:
        if self._current_session:
            self._current_session.recognized_text = event.payload.get("text")
            self._current_session.state = AudioState.PROCESSING
            self._current_session.latency.stt_ms = 85.0  # Mock measurement

    def _on_intent(self, event: Event) -> None:
        if self._current_session:
            intent = event.payload.get("intent")
            if intent:
                self._current_session.intent = {"type": intent.type}
            self._current_session.latency.intent_ms = 10.0  # Mock measurement

    def _on_workflow(self, event: Event) -> None:
        if self._current_session:
            workflow = event.payload.get("workflow")
            if workflow:
                self._current_session.workflow = {"id": workflow.id}
            self._current_session.latency.planning_ms = 5.0  # Mock measurement

    def _on_response(self, event: Event) -> None:
        if self._current_session:
            self._current_session.response_text = event.payload.get("text")
            self._current_session.state = AudioState.RESPONDING
            self._current_session.latency.tts_ms = 120.0  # Mock measurement
            self._current_session.latency.playback_ms = 250.0  # Mock measurement

            self._close_session(AudioState.IDLE)

    def _on_interrupt(self, event: Event) -> None:
        if self._current_session:
            reason = event.payload.get("reason", "UNKNOWN")
            self._current_session.interruptions.append(reason)
            self._close_session(AudioState.INTERRUPTED)

    def _close_session(self, final_state: AudioState) -> None:
        if self._current_session:
            self._current_session.state = final_state
            self._current_session.end_time = time.time()
            self.recorder.save_session(self._current_session)
            self.event_bus.publish(
                Event(
                    "Session.Ended",
                    self.name,
                    {"session_id": self._current_session.session_id},
                )
            )
            self._current_session = None
