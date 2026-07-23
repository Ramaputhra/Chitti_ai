from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter


class EchoCapability(ICapability):
    """Simple capability that echoes input. Used for validating the OS execution pipeline."""
    
    def __init__(self):
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "EchoCapability"

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
            name="echo",
            version="1.0",
            category="core",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="echo", 
                description="Echos back the provided text exactly.", 
                parameters=[ToolParameter(name="text", type="string", description="The text to echo.", required=True)]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "echo" and "text" in invocation.parameters

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(success=False, error="Invalid invocation.", output=None)

        text = invocation.parameters.get("text", "")
        return ExecutionResult(success=True, output=text)

    def cancel(self, invocation_id: str) -> None:
        pass
