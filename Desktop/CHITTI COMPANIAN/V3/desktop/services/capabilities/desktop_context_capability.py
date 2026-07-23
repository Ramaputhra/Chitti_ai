from typing import Any, Dict

import psutil

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import DocumentArtifact
from desktop.platform.shared.models.capability import CapabilityDescriptor


class DesktopContextCapability(ICapability):
    """
    Fetches the current state of the desktop (battery, system load, active workspace).
    """
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "DesktopContextCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def execute(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "query":
            return self.query_context()
        raise NotImplementedError(f"Action {action} not supported by {self.name}")

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Fetch desktop context such as battery and active workspace.",
            actions=["query"],
        )

    def query_context(self) -> DocumentArtifact:
        # Mocking active workspace for now. In a real scenario, use OS specific APIs (e.g. pygetwindow)
        active_window = "Unknown"
        try:
            # Placeholder for actual win32gui / pygetwindow logic
            import pygetwindow as gw
            active = gw.getActiveWindow()
            if active:
                active_window = active.title
        except ImportError:
            pass
        
        battery = psutil.sensors_battery()
        battery_status = f"{battery.percent}%" if battery else "Unknown"
        plugged = "Plugged In" if battery and battery.power_plugged else "On Battery"
        
        content = f"Battery: {battery_status} ({plugged}).\nActive Workspace: {active_window}."
        
        return DocumentArtifact(
            source=self.name,
            capability="DesktopContextCapability",
            content=content
        )
