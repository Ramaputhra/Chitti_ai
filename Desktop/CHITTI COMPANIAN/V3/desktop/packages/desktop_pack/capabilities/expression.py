from typing import Any, Dict
from datetime import datetime
from uuid import uuid4
from desktop.packages.sdk.pack_metadata import CapabilityMetadata
from desktop.models.presentation import RenderedExpression

class ExpressionCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Expression", supports_undo=False)
        self.event_bus = None # Injected by executor or registry if needed

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        expression_type = context.payload.get("expression_type", "unknown")
        duration = context.payload.get("duration", 0.0)
        
        if context.logger:
            context.logger.info(f"[ExpressionCapability] Triggering {expression_type} for {duration}s")
            
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        return ExecutionResult(status=ExecutionStatus.SUCCESS)

class SpeakCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Expression", supports_undo=False)
        self.event_bus = None

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        text = context.payload.get("text", "")
        
        if context.logger:
            context.logger.info(f"[SpeakCapability] Speaking: {text}")
            
        if self.event_bus:
            self.event_bus.publish(RenderedExpression(
                timestamp=datetime.now(),
                correlation_id=str(uuid4()),
                formats={"text": text, "speech": True}
            ))
            
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        return ExecutionResult(status=ExecutionStatus.SUCCESS)

class TextResponseCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Expression", supports_undo=False)
        self.event_bus = None

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        text = context.payload.get("text", "")
        
        if context.logger:
            context.logger.info(f"[TextResponseCapability] Responding: {text}")
            
        if self.event_bus:
            self.event_bus.publish(RenderedExpression(
                timestamp=datetime.now(),
                correlation_id=str(uuid4()),
                formats={"text": text}
            ))
            
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        return ExecutionResult(status=ExecutionStatus.SUCCESS)
