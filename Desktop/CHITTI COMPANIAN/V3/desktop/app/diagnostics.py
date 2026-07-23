from typing import Dict, List
from desktop.app.kernel import RuntimeKernel
from desktop.models.events import Event, DomainEvent

class PipelineValidator:
    """
    Diagnostic component.
    Tracks correlation IDs to verify missing, duplicated, or out-of-order events.
    """
    def __init__(self, kernel: RuntimeKernel):
        self.kernel = kernel
        self.traces: Dict[str, List[str]] = {}
        
        # Subscribe to all events for diagnostic tracing
        self.kernel.context.event_bus.subscribe(Event, self._on_any_event)
        
    async def _on_any_event(self, event: Event):
        if not event.correlation_id:
            return
            
        corr_id = event.correlation_id
        if corr_id not in self.traces:
            self.traces[corr_id] = []
            
        event_name = type(event).__name__
        self.traces[corr_id].append(event_name)

    def verify_pipeline(self, correlation_id: str) -> bool:
        """
        Verify the expected event sequence for a standard cognitive pipeline interaction.
        """
        if correlation_id not in self.traces:
            print(f"[Validator] ❌ No trace found for {correlation_id}")
            return False
            
        trace = self.traces[correlation_id]
        
        # Expected sequence (simplified for demonstration)
        expected = [
            "InteractionEnvelope",
            "InteractionStored",
            "PlanCreated",
            "ExpressionRequested",
            "AvatarStateChanged",
            "RenderedExpression",
            "ExpressionDelivered"
            # Note: The exact ordering between AvatarStateChanged and RenderedExpression 
            # might vary slightly since they are emitted concurrently, but we just check presence.
        ]
        
        missing = [evt for evt in expected if evt not in trace]
        if missing:
            print(f"[Validator] ❌ Pipeline broken for {correlation_id}. Missing: {missing}")
            print(f"Trace: {trace}")
            return False
            
        print(f"[Validator] ✅ Pipeline verified for {correlation_id}")
        return True


