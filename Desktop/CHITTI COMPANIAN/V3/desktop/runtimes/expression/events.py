import time
import uuid
from typing import Optional, Dict, Any
from desktop.platform.shared.interfaces.event_bus import Event

class ExpressionRequested(Event):
    """
    Emitted by the Expression Runtime when a new expression is requested from the PresenceEngine,
    before scheduling takes place. Useful for telemetry and profiling.
    """
    def __init__(self, expression_id: str):
        super().__init__(
            event_id="Expression.Requested",
            source="ExpressionRuntime",
            payload={
                "expression_id": expression_id
            }
        )
        self.expression_id = expression_id

class ExpressionStarted(Event):
    """
    Emitted by the Expression Runtime when a new expression begins.
    Subscribed to by the Output Runtimes (Visual, Audio, Servo, etc.).
    """
    def __init__(self, expression_id: str, outputs: Dict[str, Any], interruptible: bool = True):
        super().__init__(
            event_id="Expression.Started",
            source="ExpressionRuntime",
            payload={
                "expression_id": expression_id,
                "outputs": outputs,
                "interruptible": interruptible
            }
        )
        self.expression_id = expression_id
        self.outputs = outputs
        self.interruptible = interruptible

class ExpressionFinished(Event):
    """
    Emitted by the Expression Runtime when a non-interruptible expression completes naturally.
    """
    def __init__(self, expression_id: str):
        super().__init__(
            event_id="Expression.Finished",
            source="ExpressionRuntime",
            payload={
                "expression_id": expression_id
            }
        )
        self.expression_id = expression_id

class ExpressionInterrupted(Event):
    """
    Emitted by the Expression Runtime when a running expression is forcefully interrupted by a higher priority one.
    """
    def __init__(self, previous_expression_id: str, by_expression_id: str):
        super().__init__(
            event_id="Expression.Interrupted",
            source="ExpressionRuntime",
            payload={
                "previous_expression_id": previous_expression_id,
                "by_expression_id": by_expression_id
            }
        )
        self.previous_expression_id = previous_expression_id
        self.by_expression_id = by_expression_id
