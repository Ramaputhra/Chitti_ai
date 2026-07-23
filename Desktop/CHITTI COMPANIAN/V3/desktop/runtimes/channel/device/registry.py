from typing import Dict, Optional
from desktop.runtimes.channel.models.core import TrustedDevice

class DeviceRegistry:
    """Manages trusted devices on the desktop."""
    def __init__(self):
        self.devices: Dict[str, TrustedDevice] = {}
        
    def register_device(self, device: TrustedDevice):
        self.devices[device.device_id] = device
        print(f"[DeviceRegistry] Registered trusted device: {device.device_name}")
        
    def get_device(self, device_id: str) -> Optional[TrustedDevice]:
        return self.devices.get(device_id)

    def validate_token(self, device_id: str, token: str) -> bool:
        device = self.get_device(device_id)
        if not device:
            return False
        return device.permanent_token == token

    def remove_device(self, device_id: str):
        if device_id in self.devices:
            del self.devices[device_id]
            print(f"[DeviceRegistry] Removed trusted device: {device_id}")
