import logging
from desktop.models.routing_models import RoutingTrace

logger = logging.getLogger(__name__)

class RoutingTelemetryPublisher:
    """
    Publishes Routing Decisions to the EventBus.
    This enables independent JSON logging, SQLite persistence, and UI Dashboards 
    without blocking execution.
    """
    def __init__(self, event_bus: any):
        # We assume event_bus is the instance of desktop.platform.events.EventBus
        self.event_bus = event_bus

    def publish_decision(self, trace: RoutingTrace) -> None:
        """
        Dispatches a ROUTING_DECISION event to all interested subscribers.
        """
        # Publish event
        try:
            self.event_bus.publish(
                "ROUTING_DECISION",
                source="AdaptiveAIRouter",
                payload={
                    "request_id": trace.request_id,
                    "service": trace.service,
                    "selected_runtime": trace.selected_runtime,
                    "selected_provider": trace.selected_provider,
                    "decision_reason": trace.decision_reason,
                    "decision_confidence": trace.decision_confidence,
                    "execution_time_ms": trace.execution_time_ms,
                    "status": trace.status
                }
            )
            logger.debug(f"Published routing telemetry for request {trace.request_id} -> {trace.selected_runtime}")
        except Exception as e:
            logger.error(f"Failed to publish routing telemetry: {e}")
