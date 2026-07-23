import logging
from desktop.runtimes.expression.events import ExpressionStarted

logger = logging.getLogger(__name__)

class VisualRuntime:
    """
    Interprets declarative visual asset symbolic names into physical UI rendering or LED patterns.
    (Rule 37: Output Independence)
    """
    def __init__(self, event_bus=None):
        if event_bus and hasattr(event_bus, "subscribe"):
            # In a real system, VisualRuntime might coordinate CompanionWidget, LEDs, and external Displays.
            # Currently, CompanionWidget directly subscribes to ExpressionStarted via ExpressionController.
            # This runtime could orchestrate non-Qt visual elements (like an OLED matrix on the robot).
            event_bus.subscribe("Expression.Started", self._handle_expression_started)
            
    def _handle_expression_started(self, event: ExpressionStarted):
        """Reacts to a coordinated expression request."""
        visual_config = event.outputs.get("visual", {})
        animation_id = visual_config.get("animation")
        
        if animation_id:
            self._render_visuals(animation_id)

    def _render_visuals(self, animation_id: str):
        # Example: Send command over serial to LED matrix
        # logger.info(f"[Visual Runtime] Rendering animation {animation_id} to external displays")
        pass
