from PySide6.QtCore import QObject, Signal
from desktop.runtimes.expression.events import ExpressionStarted

class ExpressionController(QObject):
    """
    Thread-safe bridge between the EventBus (Background Thread) 
    and the Companion Widget (Main Thread) for Visual Expression.
    Replaces PresenceController.
    """
    # Qt Signal carrying the animation id string
    animation_started_signal = Signal(str)

    def __init__(self, event_bus=None, parent=None):
        super().__init__(parent)
        if event_bus and hasattr(event_bus, "subscribe"):
            event_bus.subscribe("Expression.Started", self._on_expression_started)

    def _on_expression_started(self, event: ExpressionStarted):
        """
        Called when the ExpressionRuntime decides to play an expression.
        We safely marshal the visual animation ID to the UI thread.
        """
        visual_config = event.outputs.get("visual", {})
        animation_id = visual_config.get("animation")
        
        if animation_id:
            self.animation_started_signal.emit(animation_id)
