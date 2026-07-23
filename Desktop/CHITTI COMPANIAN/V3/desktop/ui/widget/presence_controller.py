from PySide6.QtCore import QObject, Signal
from desktop.ui.presence.presence_state import PresenceState, PresenceStateChanged

class PresenceController(QObject):
    """
    Thread-safe bridge between the EventBus (Background Thread) 
    and the Companion Widget (Main Thread).
    """
    # Define a Qt Signal that carries the PresenceState Enum
    # Qt will automatically marshal this across threads if the receiver is on the Main Thread.
    state_changed_signal = Signal(object)

    def __init__(self, event_bus=None, parent=None):
        super().__init__(parent)
        if event_bus and hasattr(event_bus, "subscribe"):
            event_bus.subscribe("Presence.StateChanged", self._on_presence_state_changed)

    def _on_presence_state_changed(self, event: PresenceStateChanged):
        """
        Called when the EventBus broadcasts a PresenceStateChanged event.
        We emit a Qt Signal to safely transfer control to the UI thread.
        """
        self.state_changed_signal.emit(event.current)

    def on_state_changed_from_engine(self, state: str):
        """Called directly by the local PresenceEngine mock."""
        self.state_changed_signal.emit(state)
