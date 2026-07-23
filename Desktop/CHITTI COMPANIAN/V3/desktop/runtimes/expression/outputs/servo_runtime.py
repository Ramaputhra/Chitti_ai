import logging
from desktop.runtimes.expression.events import ExpressionStarted

logger = logging.getLogger(__name__)

class ServoRuntime:
    """
    Interprets declarative servo motion symbolic names into physical angles.
    (Rule 37: Output Independence)
    """
    def __init__(self, event_bus=None):
        if event_bus and hasattr(event_bus, "subscribe"):
            event_bus.subscribe("Expression.Started", self._handle_expression_started)
            
    def _handle_expression_started(self, event: ExpressionStarted):
        """Reacts to a coordinated expression request."""
        servo_config = event.outputs.get("servo", {})
        motion_id = servo_config.get("motion")
        
        if motion_id:
            self._execute_motion(motion_id)

    def _execute_motion(self, motion_id: str):
        # In a real system, this maps "nod_small" -> a sequence of [angle, time] pairs
        logger.info(f"[Servo Runtime] Executing motion sequence: {motion_id}")
        
    def _write_angle(self, servo_id: int, angle: int):
        """Low-level command logic (UART/PySerial) completely hidden from outside world."""
        pass
