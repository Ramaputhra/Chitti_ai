from typing import Dict, Any
from desktop.runtimes.channel.models.core import ChannelType

class OutputRouter:
    """
    Routes semantic responses from the Behavior Runtime to the appropriate active channel.
    """
    def __init__(self):
        self.active_channel = ChannelType.VOICE # Default
        
    def set_active_channel(self, channel: ChannelType):
        self.active_channel = channel
        print(f"[OutputRouter] Active channel changed to {channel.value}")
        
    def route_output(self, semantic_response: str, metadata: Dict[str, Any] = None):
        """
        Routes the final behavior output to the currently active channel.
        Replaces direct TTS invocations from the Behavior Engine.
        """
        print(f"[OutputRouter] Routing output to {self.active_channel.value}...")
        
        if self.active_channel == ChannelType.VOICE:
            self._route_to_tts(semantic_response)
        elif self.active_channel == ChannelType.DESKTOP_UI:
            self._route_to_desktop_ui(semantic_response)
        elif self.active_channel == ChannelType.MOBILE_CHAT:
            self._route_to_websocket(semantic_response, metadata)

    def stream_task_timeline_event(self, task_id: str, status: str, step: str, progress: int, eta: int = 0, verification: str = "PASSED") -> dict:
        """Streams structured task timeline events to the mobile UI."""
        payload = {
            "type": "TASK_TIMELINE_EVENT",
            "task_id": task_id,
            "status": status, # Task Started, Current Step, Progress %, Completed, Failed, Cancelled
            "current_step": step,
            "progress_percent": progress,
            "eta_seconds": eta,
            "verification_result": verification
        }
        print(f"[OutputRouter] Task Timeline Event: {payload}")
        return payload

    def send_priority_notification(self, title: str, message: str, priority: str = "INFO") -> dict:
        """Sends priority-mapped notifications to mobile clients."""
        payload = {
            "type": "NOTIFICATION",
            "title": title,
            "message": message,
            "priority": priority # INFO, SUCCESS, WARNING, ERROR, CRITICAL, PROGRESS, ACTION_REQUIRED
        }
        print(f"[OutputRouter] Priority Notification [{priority}]: {title} - {message}")
        return payload
            
    def _route_to_tts(self, text: str):
        print(f"[TTS Engine] Speaking: {text}")
        
    def _route_to_desktop_ui(self, text: str):
        print(f"[Desktop UI] Displaying: {text}")
        
    def _route_to_websocket(self, text: str, metadata: Dict[str, Any] = None):
        print(f"[WebSocket Transport] Pushing chat message to Android: {text}")

