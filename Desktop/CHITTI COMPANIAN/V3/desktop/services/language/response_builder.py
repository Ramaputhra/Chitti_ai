from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.response import IResponseBuilder
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.speaker import ISpeakerManager
from desktop.platform.shared.interfaces.speech import ISpeechSynthesizer
from desktop.platform.shared.models.audio import AudioPacket


class ResponseBuilder(IResponseBuilder):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        speech_synthesizer: ISpeechSynthesizer,
        speaker: ISpeakerManager,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.synthesizer = speech_synthesizer
        self.speaker = speaker
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "ResponseBuilder"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe("WorkflowStep.GenerateResponse", self._on_generate)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def _on_generate(self, event: Event) -> None:
        params = event.payload.get("parameters", {})
        template = params.get("template", "Unknown")

        response_text = "I'm not sure how to respond to that."

        # ── Named templates (mock responses for Sprint 13) ────────────────────
        if template == "Greeting":
            response_text = "Hello! How can I help you today?"
        elif template == "Identity":
            response_text = "I am Chitti, your AI Companion."
        elif template == "Gratitude":
            response_text = "You're very welcome!"
        elif template == "Farewell":
            response_text = "Goodbye! Have a great day."

        # ── Universal primitives (Speak / AskQuestion carry explicit text) ────
        elif template in ("Direct", "AskQuestion"):
            # The executor already resolved the text — use it directly
            response_text = params.get("text", response_text)

        self.logger.info(f"Generated Response: {response_text}")


        self.event_bus.publish(
            Event(
                SystemEvents.RESPONSE_GENERATED,
                self.name,
                {"text": response_text},
            )
        )

        # Dispatch string to Speech Synthesizer (TTS), then raw AudioPacket to Speaker
        raw_pcm_bytes = self.synthesizer.synthesize(response_text)
        if raw_pcm_bytes:
            import time
            sample_rate = 16000  # Based on piper model json config
            channels = 1
            bit_depth = 16
            bytes_per_sample = bit_depth // 8
            frame_count = len(raw_pcm_bytes) // (channels * bytes_per_sample)
            duration = frame_count / sample_rate
            
            audio_packet = AudioPacket(
                timestamp=time.time(),
                sample_rate=sample_rate,
                channels=channels,
                bit_depth=bit_depth,
                frame_count=frame_count,
                duration=duration,
                data=raw_pcm_bytes
            )
            self.speaker.play(audio_packet)
        else:
            self.logger.warning("Failed to synthesize TTS audio.")
