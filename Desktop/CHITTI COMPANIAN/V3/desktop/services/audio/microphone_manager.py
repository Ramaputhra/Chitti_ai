import time
from typing import Any, Dict

import numpy as np
import sounddevice as sd

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.audio_devices import IAudioDeviceManager
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.microphone import IMicrophoneManager
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.audio import AudioPacket


class MicrophoneManager(IMicrophoneManager):
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
        self._stream = None
        self._sample_rate = 16000
        self._channels = 1

    @property
    def name(self) -> str:
        return "MicrophoneManager"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.logger.info(f"{self.name} initialized")

    def start(self) -> None:
        if self._state == ServiceState.STOPPED:
            self._state = ServiceState.RUNNING

    def pause(self) -> None:
        self.stop_capture()
        self._state = ServiceState.STOPPED

    def resume(self) -> None:
        self._state = ServiceState.RUNNING
        self.start_capture()

    def recover(self) -> None:
        self.logger.info(f"{self.name} attempting recovery...")
        self.stop_capture()
        self._state = ServiceState.STOPPED
        self.initialize()
        self.start()
        # Attempt to restart capture, if mic is still unplugged, it will fail gracefully
        self.start_capture()

    def shutdown(self) -> None:
        self.stop_capture()
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"stream_active": self._stream is not None and self._stream.active}

    def start_capture(self) -> None:
        if self._stream and self._stream.active:
            return

        device_id = self.device_manager.current_input()

        def audio_callback(
            indata: np.ndarray, frames: int, time_info: Any, status: Any
        ) -> None:
            if status:
                self.logger.warning(f"Audio stream status: {status}")

            packet = AudioPacket(
                timestamp=time.time(),
                sample_rate=self._sample_rate,
                channels=self._channels,
                bit_depth=16,
                frame_count=frames,
                duration=frames / self._sample_rate,
                data=indata.tobytes(),
            )
            self.event_bus.publish(
                Event(
                    event_id=SystemEvents.VOICE_AUDIO_FRAME,
                    source=self.name,
                    payload={"packet": packet},
                )
            )

        try:
            self._stream = sd.InputStream(
                device=device_id,
                channels=self._channels,
                samplerate=self._sample_rate,
                dtype="int16",
                callback=audio_callback,
            )
            self._stream.start()
            self.logger.info("Microphone capture started")
            self.event_bus.publish(
                Event(SystemEvents.VOICE_CAPTURE_STARTED, self.name, {})
            )
        except Exception as e:
            self.logger.exception(e, module=self.name)
            self.event_bus.publish(
                Event(SystemEvents.VOICE_ERROR, self.name, {"error": str(e)})
            )

    def stop_capture(self) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self.logger.info("Microphone capture stopped")
            self.event_bus.publish(
                Event(SystemEvents.VOICE_CAPTURE_STOPPED, self.name, {})
            )
