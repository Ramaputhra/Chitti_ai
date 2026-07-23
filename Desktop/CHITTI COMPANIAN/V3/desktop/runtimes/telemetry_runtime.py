from datetime import datetime
from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.events import ExecutionCompletedEvent, ExecutionTelemetryEvent
from desktop.models.telemetry import ExecutionTelemetry

class TelemetryRuntime(IRuntime):
    """
    Observes execution events and emits typed telemetry objects via EventBus.
    Keeps ExecutionRuntime pure and isolated from telemetry concerns.
    """
    def __init__(self):
        self.context = None

    @property
    def dependencies(self):
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        context.event_bus.subscribe(ExecutionCompletedEvent, self._on_execution_completed)
        return True

    async def start(self) -> bool:
        print("    [TelemetryRuntime] Started. Listening for execution events.")
        return True

    async def stop(self) -> bool:
        print("    [TelemetryRuntime] Stopped.")
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    async def _on_execution_completed(self, event: ExecutionCompletedEvent):
        """Transforms ExecutionCompletedEvent into ExecutionTelemetryEvent."""
        metadata = event.metadata
        
        # Extract target from parameters if possible
        parameters = metadata.get("parameters", {})
        target = None
        if isinstance(parameters, dict):
            # Best effort target extraction
            target = parameters.get("destination") or parameters.get("path") or parameters.get("source")
            
        telemetry_payload = ExecutionTelemetry(
            capability=metadata.get("capability", "unknown"),
            duration_ms=metadata.get("duration_ms", 0),
            status=metadata.get("status", "UNKNOWN"),
            verification=metadata.get("verification", False),
            target=target
        )
        
        telemetry_event = ExecutionTelemetryEvent(
            timestamp=datetime.now(),
            source="TelemetryRuntime",
            correlation_id=event.correlation_id,
            event_type="EXECUTION_TELEMETRY",
            metadata={"telemetry": telemetry_payload}
        )
        
        # Emit typed telemetry
        await self.context.event_bus.publish(telemetry_event)
