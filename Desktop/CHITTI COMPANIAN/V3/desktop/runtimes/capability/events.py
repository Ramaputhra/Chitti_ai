from desktop.platform.shared.interfaces.event_bus import Event
from typing import Dict, Any

class CapabilityExecuted(Event):
    def __init__(self, tool: str, status: str, error_message: str = None, metadata: Dict[str, Any] = None, session_id: str = "default"):
        payload = {
            "tool": tool,
            "status": status,
            "error_message": error_message,
            "metadata": metadata or {},
            "session_id": session_id
        }
        super().__init__("CapabilityExecuted", "CapabilityRuntime", payload)
