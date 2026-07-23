from desktop.runtimes.channel.models.core import PresenceState, ChannelType
from desktop.runtimes.channel.router.output import OutputRouter

class PresenceManager:
    """
    Manages Companion Presence Mode. 
    It doesn't directly disable STT/WakeWord; it publishes events 
    that the respective runtimes listen to.
    """
    def __init__(self, output_router: OutputRouter):
        self.state = PresenceState.IDLE
        self.output_router = output_router
        
    def handle_mobile_connected(self):
        """Triggered when the Android app establishes an active WebSocket session."""
        print("[PresenceManager] Mobile Connected. Entering Companion Presence Mode.")
        self.state = PresenceState.MOBILE_ACTIVE
        self.output_router.set_active_channel(ChannelType.MOBILE_CHAT)
        
        self._publish_event("CompanionModeChanged", {"active": True, "channel": "mobile"})
        
    def handle_mobile_disconnected(self):
        """Triggered when the Android app disconnects, times out, or logs out."""
        print("[PresenceManager] Mobile Disconnected. Restoring Desktop Mode.")
        self.state = PresenceState.IDLE
        self.output_router.set_active_channel(ChannelType.VOICE)
        
        self._publish_event("CompanionModeChanged", {"active": False, "channel": "desktop"})
        
    def _publish_event(self, event_name: str, payload: dict):
        """
        Publishes to the global EventBus.
        Wake Word Runtime listens to this and suspends itself.
        STT Runtime suspends itself.
        Presentation Engine renders the 'Chatting on Mobile' overlay.
        """
        print(f"[EventBus] Emitting {event_name}: {payload}")
