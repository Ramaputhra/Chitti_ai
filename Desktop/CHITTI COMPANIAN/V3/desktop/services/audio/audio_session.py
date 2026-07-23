from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.audio_pipeline import IAudioPipeline
from desktop.platform.shared.interfaces.audio_session import IAudioSession
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.microphone import IMicrophoneManager
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.speaker import ISpeakerManager
from desktop.platform.shared.interfaces.wake_word import IWakeWordProvider


class AudioSession(IAudioSession):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        microphone: IMicrophoneManager,
        speaker: ISpeakerManager,
        pipeline: IAudioPipeline,
        wake_word_provider: IWakeWordProvider,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.microphone = microphone
        self.speaker = speaker
        self.pipeline = pipeline
        self.wake_word_provider = wake_word_provider
        self._state = ServiceState.STOPPED

        self._muted = False
        self._ducking_enabled = True

    @property
    def name(self) -> str:
        return "AudioSession"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(
            SystemEvents.VOICE_PLAYBACK_STARTED, self._on_playback_started
        )
        self.event_bus.subscribe(
            SystemEvents.VOICE_PLAYBACK_FINISHED, self._on_playback_finished
        )
        self.event_bus.subscribe("Session.Ended", self._on_session_ended)
        self.event_bus.subscribe("Session.Started", self._on_session_started)
        
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

        if not self._muted:
            self.microphone.start_capture()
            self.wake_word_provider.start_listening()

    def _on_session_started(self, event: Event) -> None:
        # Don't listen for wake word during active session
        self.wake_word_provider.stop_listening()
        
    def _on_session_ended(self, event: Event) -> None:
        if not self._muted:
            self.wake_word_provider.start_listening()

    def shutdown(self) -> None:
        self.wake_word_provider.stop_listening()
        self.microphone.stop_capture()
        self.speaker.stop_playback()
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"muted": self._muted, "ducking_enabled": self._ducking_enabled}

    def mute_microphone(self) -> None:
        self._muted = True
        self.microphone.stop_capture()
        self.logger.info("Microphone muted globally")

    def unmute_microphone(self) -> None:
        self._muted = False
        self.microphone.start_capture()
        self.logger.info("Microphone unmuted globally")

    def set_ducking(self, enabled: bool) -> None:
        self._ducking_enabled = enabled
        self.logger.info(f"Audio ducking set to {enabled}")

    def _on_playback_started(self, event: Event) -> None:
        if self._ducking_enabled and not self._muted:
            self.microphone.stop_capture()
            self.logger.info(
                "Ducking enabled: Microphone temporarily stopped during playback"
            )

    def _on_playback_finished(self, event: Event) -> None:
        if self._ducking_enabled and not self._muted:
            self.microphone.start_capture()
            self.logger.info("Playback finished: Microphone resumed")
