import logging
from desktop.ui.presence.presence_state import PresenceState, PresenceStateChanged

logger = logging.getLogger(__name__)

class ServoController:
    """
    Mock Hardware Controller that syncs servo motors with PresenceState changes.
    Subscribes directly to PresenceStateChanged events from the EventBus (Rule 34).
    """
    def __init__(self, event_bus=None):
        if event_bus and hasattr(event_bus, "subscribe"):
            event_bus.subscribe("Presence.StateChanged", self._handle_presence_state_changed)
            
    def _handle_presence_state_changed(self, event: PresenceStateChanged):
        """Reacts to state changes published by PresenceEngine."""
        self.play_state(event.current)

    def play_state(self, state: PresenceState):
        if state == PresenceState.IDLE:
            self._execute_idle_motion()
        elif state == PresenceState.READY:
            self._execute_neutral_forward()
        elif state == PresenceState.LISTENING:
            self._execute_look_up()
        elif state == PresenceState.WORKING:
            self._execute_busy_jitter()
        elif state == PresenceState.SUCCESS:
            self._execute_quick_nod()
        elif state == PresenceState.FAILURE or state == PresenceState.ERROR:
            self._execute_shake_head()
        elif state == PresenceState.TALKING:
            self._execute_talking_tilt()
        elif state == PresenceState.SLEEPING:
            self._execute_head_down()

    def play_event(self, event_name: str):
        if event_name.lower() == "yeah":
            self._execute_quick_nod()
        else:
            logger.info(f"[Mock Hardware] Executing event servo sequence: {event_name}")

    # Internal abstract behaviors mapping to specific angles
    
    def _execute_idle_motion(self):
        logger.info("[Mock Hardware] Initiating slow random panning routine.")
        # E.g., self._write_angle(1, random.randint(45, 135))
        
    def _execute_neutral_forward(self):
        logger.info("[Mock Hardware] Resetting to neutral forward.")
        
    def _execute_look_up(self):
        logger.info("[Mock Hardware] Looking up and centering (Attentive).")
        
    def _execute_busy_jitter(self):
        logger.info("[Mock Hardware] Jittering / busy motion.")
        
    def _execute_quick_nod(self):
        logger.info("[Mock Hardware] Quick Nod (Yes).")
        
    def _execute_shake_head(self):
        logger.info("[Mock Hardware] Shake Head (No).")
        
    def _execute_talking_tilt(self):
        logger.info("[Mock Hardware] Animating Head Tilt (Speaking).")
        
    def _execute_head_down(self):
        logger.info("[Mock Hardware] Head Down (Resting).")

    def _write_angle(self, servo_id: int, angle: int):
        """Low-level command logic (UART/PySerial) completely hidden from outside world."""
        pass
