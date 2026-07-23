import logging
import time
from typing import Any, Dict

from desktop.models.presentation_models import PresenceState, PresenceStateChangedEvent

logger = logging.getLogger(__name__)

class PresenceRuntime:
    """
    Implements the desktop lifecycle state machine for the CHITTI avatar.
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self.state = PresenceState.EDGE_DOCKED_IDLE

    def transition_to(self, new_state: PresenceState) -> None:
        if self.state == new_state:
            return
            
        old_state = self.state
        self.state = new_state
        logger.info(f"Presence Engine: State transition {old_state.name} -> {self.state.name}")
        
        event = PresenceStateChangedEvent(
            old_state=old_state,
            new_state=self.state,
            timestamp=time.time()
        )
        self.event_bus.publish("PRESENCE_STATE_CHANGED", source="PresenceRuntime", payload={"event": event})

    def handle_workflow_started(self):
        self.transition_to(PresenceState.TASK_EXECUTION)

    def handle_workflow_minimized(self):
        if self.state == PresenceState.TASK_EXECUTION:
            self.transition_to(PresenceState.EDGE_DOCKED_WORKING)

    def handle_workflow_completed(self):
        # By default, open the follow-up window when a task finishes
        self.transition_to(PresenceState.FOLLOW_UP_WINDOW)
        
    def handle_idle_timeout(self, seconds: int):
        if seconds >= 120 and self.state == PresenceState.RELAXED_IDLE:
            self.transition_to(PresenceState.GOODBYE)
            time.sleep(2) # Finish goodbye animation
            self.transition_to(PresenceState.RESIDENT_MODE)
        elif seconds >= 20 and self.state == PresenceState.EDGE_DOCKED_IDLE:
            self.transition_to(PresenceState.RELAXED_IDLE)
