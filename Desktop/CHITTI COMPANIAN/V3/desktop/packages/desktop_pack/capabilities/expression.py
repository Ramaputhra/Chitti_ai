from typing import Any, Dict
from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ExpressionCapability:
    """
    Expression capability - triggers expressions without publishing events directly.
    ExpressionRuntime should handle the rendering via ExpressionRequested events.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Expression", supports_undo=False)

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        expression_type = context.payload.get("expression_type", "unknown")
        duration = context.payload.get("duration", 0.0)
        
        if context.logger:
            context.logger.info(f"[ExpressionCapability] Triggering {expression_type} for {duration}s")
            
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        return ExecutionResult(status=ExecutionStatus.SUCCESS)

class SpeakCapability:
    """
    Speak capability - returns speech text for ExpressionRuntime to render.
    Does not publish events directly.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Expression", supports_undo=False)

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        
        text = context.payload.get("text", "")
        
        if context.logger:
            context.logger.info(f"[SpeakCapability] Returning text for rendering: {text}")
        
        # Return text in outputs - ExpressionRuntime will render via ExpressionRequested
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            outputs={"text": text, "modality": "speech"}
        )

class TextResponseCapability:
    """
    Text response capability - returns text for ExpressionRuntime to render.
    Does not publish events directly.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Expression", supports_undo=False)

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        
        text = context.payload.get("text", "")
        
        if context.logger:
            context.logger.info(f"[TextResponseCapability] Returning text for rendering: {text}")
        
        # Return text in outputs - ExpressionRuntime will render via ExpressionRequested
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            outputs={"text": text, "modality": "text"}
        )
