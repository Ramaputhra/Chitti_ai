import asyncio
import logging
from typing import Any
from desktop.runtimes.expression.events import ExpressionRequested
from desktop.ui.presence.presence_state import PresenceStateChanged
from desktop.runtimes.expression.manifest_loader import ExpressionManifestLoader
from desktop.runtimes.expression.scheduler import ExpressionScheduler

logger = logging.getLogger(__name__)

class ExpressionRuntime:
    """
    Consumes declarative Presence events and schedules multi-modal expressions.
    (Rule 37: Expression Runtime Coordination)
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self.manifest_loader = ExpressionManifestLoader()
        self.scheduler = ExpressionScheduler(self.event_bus)
        
        if hasattr(self.event_bus, "subscribe"):
            # Subscribe to the string event ID as published by PresenceEngine
            self.event_bus.subscribe("Presence.StateChanged", self._on_presence_state_changed)

    def start(self):
        self.scheduler.start()
        logger.info("Expression Runtime started.")

    def stop(self):
        self.scheduler.stop()
        logger.info("Expression Runtime stopped.")

    def _on_presence_state_changed(self, event: PresenceStateChanged):
        """Reacts to a cognitive state change and maps it to a physical expression."""
        state_name = event.current.name
        
        # 1. Load declarative manifest for this state (Rule 38)
        manifest = self.manifest_loader.get_expression(state_name)
        
        # Emit telemetry event
        if hasattr(self.event_bus, "publish"):
            self.event_bus.publish(ExpressionRequested(expression_id=manifest.get("id")))
        
        # 2. Schedule it (enforcing minimum durations and interruptions)
        self.scheduler.schedule(manifest)
