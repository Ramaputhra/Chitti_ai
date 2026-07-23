from desktop.models.capability import CapabilityResult, CapabilityAction
from desktop.app.capability_contracts import ICapability, CapabilityDescriptor
from desktop.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
import webbrowser

class RenderResultCapability(ICapability):
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        # Fetch last capability result from context memory
        result_obj = None
        
        if hasattr(context, "episodes"):
            for ep in reversed(context.episodes):
                if hasattr(ep, "metadata") and "capability_result" in ep.metadata:
                    result_obj = ep.metadata["capability_result"]
                    break
                    
        if not result_obj:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="I don't have a previous result to display yet.")
            
        template_name = getattr(result_obj, "template_name", None)
        template_data = getattr(result_obj, "template_data", {})
        
        if not template_name:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="Previous result cannot be displayed visually.")
        
        from desktop.app.context import EventBus
        event_bus = context.services.resolve(EventBus)
        from desktop.platform.shared.interfaces.event_bus import Event
        
        event_bus.publish(Event("UI.RenderTemplate", "RenderResultCapability", {
            "template_name": template_name,
            "template_data": template_data
        }))
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"rendered": True})

def get_render_capability_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        id="RenderResultCapability",
        version="1.0.0",
        permissions=["ui"],
        execution_mode="async",
        factory=RenderResultCapability
    )

class ExecuteResultActionCapability(ICapability):
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        action = context.workflow.parameters.get("action", "")
        url = context.workflow.parameters.get("url", "")
        
        if action == "OPEN_URL" and url:
            webbrowser.open(url)
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
        
        return ExecutionResult(status=ExecutionStatus.FAILED, error_message="Invalid action or URL")

def get_execute_result_capability_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        id="ExecuteResultActionCapability",
        version="1.0.0",
        permissions=["web"],
        execution_mode="async",
        factory=ExecuteResultActionCapability
    )
