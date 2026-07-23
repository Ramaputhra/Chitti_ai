from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.runtimes.presentation.models import PresentationModel
from desktop.runtimes.productivity.productivity_runtime import ProductivityRuntime

class ProductivityCapability(ICapability):
    """Provides access to the user's current behavioral understanding and productivity state."""
    
    def __init__(self, productivity_runtime: ProductivityRuntime):
        self.productivity_runtime = productivity_runtime
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "ProductivityCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="productivity",
            version="1.0",
            category="intelligence",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="get_current_productivity", 
                description="Get the user's current behavioral state, focus session, and attention confidence.", 
                parameters=[]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "get_current_productivity"

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])
            
        model: PresentationModel = self.productivity_runtime.present()
        
        summary = f"Current behavior is {model.data['focus_confidence']} confident."
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=model)

    def cancel(self, invocation_id: str) -> None:
        pass
