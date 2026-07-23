from typing import Any, Dict, List, Optional

import sounddevice as sd

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.audio_devices import IAudioDeviceManager
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.settings import ISettingsManager


class AudioDeviceManager(IAudioDeviceManager):
    """
    Interacts with PortAudio via sounddevice to list and select microphones/speakers.
    Persists preferences using the SettingsManager.
    """
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        settings: ISettingsManager,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.settings = settings
        
        # Load from settings or None
        self._input_id: Optional[int] = self.settings.get("audio.input_device", None)
        self._output_id: Optional[int] = self.settings.get("audio.output_device", None)

    def get_input_devices(self) -> List[Dict[str, Any]]:
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                devices.append({"id": i, "name": dev["name"], "channels": dev["max_input_channels"]})
        return devices

    def get_output_devices(self) -> List[Dict[str, Any]]:
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_output_channels"] > 0:
                devices.append({"id": i, "name": dev["name"], "channels": dev["max_output_channels"]})
        return devices

    def set_input_device(self, device_id: int) -> None:
        self._input_id = device_id
        self.settings.set("audio.input_device", device_id)
        self.logger.info(f"Input device set to {device_id}")
        self.event_bus.publish(
            Event(
                event_id=SystemEvents.VOICE_DEVICE_CHANGED,
                source="AudioDeviceManager",
                payload={"type": "input", "device_id": device_id},
            )
        )

    def set_output_device(self, device_id: int) -> None:
        self._output_id = device_id
        self.settings.set("audio.output_device", device_id)
        self.logger.info(f"Output device set to {device_id}")
        self.event_bus.publish(
            Event(
                event_id=SystemEvents.VOICE_DEVICE_CHANGED,
                source="AudioDeviceManager",
                payload={"type": "output", "device_id": device_id},
            )
        )

    def current_input(self) -> Optional[int]:
        return self._input_id

    def current_output(self) -> Optional[int]:
        return self._output_id
