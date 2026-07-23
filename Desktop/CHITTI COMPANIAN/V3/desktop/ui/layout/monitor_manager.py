import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MonitorManager:
    """
    S36D-1: Multi-Monitor & High DPI Scaling Manager.
    """
    def __init__(self):
        self.monitors = [
            {"index": 0, "name": "Primary Display", "resolution": "1920x1080", "dpi_scale": 1.0, "x": 0, "y": 0, "w": 1920, "h": 1080},
            {"index": 1, "name": "Secondary Display", "resolution": "2560x1440", "dpi_scale": 1.25, "x": 1920, "y": 0, "w": 2560, "h": 1440}
        ]

    def get_primary_monitor(self) -> Dict[str, Any]:
        return self.monitors[0]

    def scale_coordinate(self, val: int, monitor_index: int = 0) -> int:
        scale = self.monitors[monitor_index]["dpi_scale"] if monitor_index < len(self.monitors) else 1.0
        return int(val * scale)
