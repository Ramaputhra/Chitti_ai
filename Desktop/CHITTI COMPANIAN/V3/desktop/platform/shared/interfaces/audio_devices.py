from typing import Any, Dict, List, Optional, Protocol


class IAudioDeviceManager(Protocol):
    """
    Enumerates and manages physical audio interfaces on the OS.
    """
    def get_input_devices(self) -> List[Dict[str, Any]]:
        ...

    def get_output_devices(self) -> List[Dict[str, Any]]:
        ...

    def set_input_device(self, device_id: int) -> None:
        ...

    def set_output_device(self, device_id: int) -> None:
        ...

    def current_input(self) -> Optional[int]:
        ...

    def current_output(self) -> Optional[int]:
        ...
