from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.language import ILanguageRuntime
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.speech import ISpeechProvider
from desktop.platform.shared.models.audio import AudioPacket


class LanguageRuntime(ILanguageRuntime):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        speech_provider: ISpeechProvider,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.speech_provider = speech_provider
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "LanguageRuntime"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(SystemEvents.VOICE_AUDIO_READY, self._on_audio_ready)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def _on_audio_ready(self, event: Event) -> None:
        if self._state != ServiceState.RUNNING:
            return

        packet: AudioPacket = event.payload.get("packet")
        if not packet:
            return

        self.event_bus.publish(
            Event(SystemEvents.LANGUAGE_PROCESSING_STARTED, self.name, {})
        )

        try:
            result = self.speech_provider.transcribe(packet)
            text = result.text if hasattr(result, "text") else result  # fallback if provider still returns str
            language = result.language if hasattr(result, "language") else "en"
            confidence = result.confidence if hasattr(result, "confidence") else 1.0

            if text and text.strip():
                self.logger.info(f"Speech Recognized: {text} (lang: {language}, conf: {confidence:.2f})")
                self.event_bus.publish(
                    Event(
                        SystemEvents.LANGUAGE_TEXT_RECOGNIZED,
                        self.name,
                        {
                            "text": text,
                            "source": "audio",
                            "language": language,
                            "confidence": confidence
                        },
                    )
                )
            else:
                self.logger.warning("Empty transcription received.")
        except Exception as e:
            self.logger.exception(e, module=self.name)
        finally:
            self.event_bus.publish(
                Event(SystemEvents.LANGUAGE_PROCESSING_FINISHED, self.name, {})
            )

    def inject_text(self, text: str) -> None:
        """Allows the Developer Console to bypass audio completely."""
        if not text or not text.strip():
            return

        self.logger.info(f"Developer Injection: {text}")
        self.event_bus.publish(
            Event(
                SystemEvents.LANGUAGE_TEXT_RECOGNIZED,
                self.name,
                {"text": text, "source": "developer_console"},
            )
        )
