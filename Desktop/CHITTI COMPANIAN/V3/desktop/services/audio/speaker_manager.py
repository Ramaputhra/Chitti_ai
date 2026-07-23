import threading
from typing import Any, Dict

import numpy as np
import sounddevice as sd

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.audio_devices import IAudioDeviceManager
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.speaker import ISpeakerManager
from desktop.platform.shared.models.audio import AudioPacket


class SpeakerManager(ISpeakerManager):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        device_manager: IAudioDeviceManager,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.device_manager = device_manager
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SpeakerManager"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self.stop_playback()
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def play(self, packet: AudioPacket) -> None:
        if self._state != ServiceState.RUNNING:
            self.logger.warning("Attempted to play audio while SpeakerManager is not running.")
            return

        device_id = self.device_manager.current_output()

        audio_data = np.frombuffer(packet.data, dtype=np.int16)

        self.event_bus.publish(
            Event(SystemEvents.VOICE_PLAYBACK_STARTED, self.name, {})
        )

        def _play_thread() -> None:
            try:
                sd.play(
                    audio_data,
                    samplerate=packet.sample_rate,
                    device=device_id,
                    blocking=True,
                )
                self.event_bus.publish(
                    Event(SystemEvents.VOICE_PLAYBACK_FINISHED, self.name, {})
                )
            except Exception as e:
                self.logger.exception(e, module=self.name)
                self.event_bus.publish(
                    Event(SystemEvents.VOICE_ERROR, self.name, {"error": str(e)})
                )

        threading.Thread(target=_play_thread, daemon=True).start()

    def stop_playback(self) -> None:
        sd.stop()
