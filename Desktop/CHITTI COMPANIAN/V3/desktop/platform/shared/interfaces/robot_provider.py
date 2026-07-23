from typing import Any, Dict

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.robot_model import RobotModel


class IRobotProvider(IService):
    """
    Standard interface for all Hardware Perception Capabilities.
    Takes raw ESP32/Hardware telemetry and enriches the unified RobotModel in place.
    """
    def analyze(self, raw_telemetry: Dict[str, Any], model: RobotModel) -> None:
        """Parses hardware-specific data to update semantic states in the RobotModel."""
        ...

    def describe(self) -> Dict[str, Any]:
        """Returns metadata about the provider's capabilities."""
        ...
