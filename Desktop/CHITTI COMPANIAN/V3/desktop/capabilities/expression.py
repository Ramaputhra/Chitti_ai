from desktop.app.capability_contracts import ICapability, CapabilityDescriptor
from desktop.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.models.interaction import ExpressionRequested

class ExpressionCapability(ICapability):
    """
    Publishes an ExpressionRequested event to the EventBus.
    This separates the act of 'deciding to speak' from 'how to speak'.
    """
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        text = context.workflow.parameters.get("text", "")
        if not text:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="No text provided for expression")
            
        # Get EventBus from ServiceRegistry
        # Note: EventBus is injected via the registry for capabilities, ensuring isolation.
        from desktop.app.context import EventBus
        event_bus = context.services.resolve(EventBus)
        
        from desktop.models.interaction import ExpressionType
        req = ExpressionRequested(
            interaction_id=context.interaction_id,
            correlation_id=context.correlation_id,
            expression_type=ExpressionType.SPEAK,
            payload=text
        )
        
        event_bus.publish(req)
        
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            output_data={"expressed_text": text}
        )

def get_expression_capability_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        id="ExpressionCapability",
        version="1.0.0",
        permissions=["expression"],
        execution_mode="async",
        factory=ExpressionCapability
    )
