from typing import Any, Dict

from desktop.platform.shared.interfaces.service import IService


class IHealthMonitor(IService):
    """
    Monitors overall system health, including memory usage, CPU usage, 
    and the health status of all registered IServices.
    """
    def generate_report(self) -> Dict[str, Any]:
        ...
