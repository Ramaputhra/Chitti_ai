import time
from typing import Any, Dict

import numpy as np

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.audio_pipeline import IAudioPipeline
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.vad import IVADStrategy
from desktop.platform.shared.models.audio import AudioPacket


class AudioPipeline(IAudioPipeline):
    """
    Buffers frames between Voice.SpeechStarted and Voice.SpeechEnded.
    Emits the final Voice.AudioReady packet containing the full utterance.
    """
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        vad_strategy: IVADStrategy,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.vad = vad_strategy
        self._state = ServiceState.STOPPED

        self._is_speaking = False
        self._listening = False  # Only buffer when listening
        self._buffer = bytearray()

        self._silence_frames = 0
        # Wait approx 0.5s of silence before cutting off
        # Assuming ~30ms chunks, 15 frames is close to 0.5s
        self._max_silence_frames = 15
        
        # Hard timeout: if speech lasts longer than 15 seconds, force cutoff
        # Assuming 1024 samples per frame at 16kHz = 64ms per frame. 
        # 15 seconds / 0.064 = ~234 frames. We'll use a conservative 300 frames.
        self._max_speech_frames = 300
        self._speech_frames = 0

    @property
    def name(self) -> str:
        return "AudioPipeline"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.vad.initialize()
        self.event_bus.subscribe(SystemEvents.VOICE_AUDIO_FRAME, self._on_audio_frame)
        self.event_bus.subscribe("Session.Started", self._on_session_started)
        self.event_bus.subscribe("Session.Ended", self._on_session_ended)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def _on_session_started(self, event: Event) -> None:
        self._listening = True
        self._buffer.clear()
        self._speech_frames = 0
        self._silence_frames = 0
        self.logger.info("AudioPipeline now listening for speech.")

    def _on_session_ended(self, event: Event) -> None:
        self._listening = False
        self.logger.info("AudioPipeline stopped listening.")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"speaking": self._is_speaking, "buffer_size": len(self._buffer)}

    def _on_audio_frame(self, event: Event) -> None:
        if self._state != ServiceState.RUNNING:
            return

        packet: AudioPacket = event.payload.get("packet")
        if not packet:
            return

        audio_data = np.frombuffer(packet.data, dtype=np.int16)
        
        # We always process the frame through VAD so it can continuously adapt to background noise
        is_speech = self.vad.process_frame(audio_data)

        if not self._listening:
            return

        # Hard timeout logic
        if self._is_speaking:
            self._speech_frames += 1
            if self._speech_frames > self._max_speech_frames:
                self.logger.warning("Hard timeout reached! Forcing speech cut-off.")
                self._force_emit_ready(packet)
                return

        if is_speech:
            self._silence_frames = 0
            if not self._is_speaking:
                self._is_speaking = True
                self._speech_frames = 0
                self.event_bus.publish(
                    Event(SystemEvents.VOICE_SPEECH_STARTED, self.name, {})
                )
                self._buffer.clear()
            self._buffer.extend(packet.data)
        else:
            if self._is_speaking:
                self._buffer.extend(packet.data)
                self._silence_frames += 1

                if self._silence_frames > self._max_silence_frames:
                    self._force_emit_ready(packet)

    def _force_emit_ready(self, packet: AudioPacket) -> None:
        self._is_speaking = False
        self.event_bus.publish(
            Event(SystemEvents.VOICE_SPEECH_ENDED, self.name, {})
        )

        # Finalize buffer into a clean packet
        ready_packet = AudioPacket(
            timestamp=time.time(),
            sample_rate=packet.sample_rate,
            channels=packet.channels,
            bit_depth=packet.bit_depth,
            frame_count=len(self._buffer) // 2,  # 16-bit = 2 bytes per sample
            duration=(len(self._buffer) // 2) / packet.sample_rate,
            data=bytes(self._buffer),
        )

        self.event_bus.publish(
            Event(
                SystemEvents.VOICE_AUDIO_READY,
                self.name,
                {"packet": ready_packet},
            )
        )
        self.logger.info(
            f"Emitted AudioReady: {ready_packet.duration:.2f}s of speech"
        )
        self._buffer.clear()
        self._listening = False  # Wait for next session or prompt
