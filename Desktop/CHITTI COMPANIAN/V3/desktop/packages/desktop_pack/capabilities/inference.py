from typing import Any, Dict
from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ChatResponseCapability:
    """
    Chat response capability - handles conversational responses.
    NOTE: This is a transitional capability. Full LLM calls should go through
    InferenceRuntime in the cognitive pipeline. This returns text for rendering.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Inference", supports_undo=False)

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        """Execute chat response - returns text for ExpressionRuntime to render."""
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        
        text = context.payload.get("text", "")
        if context.logger:
            context.logger.info(f"[ChatResponseCapability] Processing response request")
        
        # Return the response text - ExpressionRuntime will handle rendering
        # This capability should be called after InferenceRuntime generates the response
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            outputs={"text": text, "needs_expression": True}
        )
