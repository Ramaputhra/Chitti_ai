import sys
import platform
from typing import List

from desktop.platform.shared.interfaces.capability import ICapability, ICapabilityRegistry
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter


class IdentityCapability(ICapability):
    """Provides information about CHITTI's identity, version, and platform."""
    
    def __init__(self, registry: ICapabilityRegistry):
        self._registry = registry
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "IdentityCapability"

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
            name="identity",
            version="1.0",
            category="core",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="get_identity", description="Get the AI's identity and core purpose.", parameters=[]),
            ToolDescriptor(name="get_version", description="Get the current software version.", parameters=[]),
            ToolDescriptor(name="get_platform_info", description="Get the underlying OS and Python version.", parameters=[]),
            ToolDescriptor(name="get_capabilities", description="List all available capabilities.", parameters=[])
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        valid_tools = [t.name for t in self.discover_tools()]
        return invocation.tool_name in valid_tools

    def execute(self, *args, **kwargs) -> ExecutionResult:
        # Adapt to both old Planner ToolInvocation and new CapabilityInvoker
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            invocation = ToolInvocation(tool_name=action, parameters=parameters)

        if not self.validate(invocation):
            return ExecutionResult(success=False, error=f"Invalid tool: {invocation.tool_name}", output=None)

        if invocation.tool_name == "get_identity" or invocation.tool_name == "identify":
            return ExecutionResult(success=True, output="I am CHITTI, a desktop AI companion operating on Platform v3.0.")
            
        elif invocation.tool_name == "get_version":
            return ExecutionResult(success=True, output="Platform Version 3.0 (Sprint 21)")
            
        elif invocation.tool_name == "get_platform_info":
            info = f"OS: {platform.system()} {platform.release()} ({platform.architecture()[0]})\nPython: {sys.version}"
            return ExecutionResult(success=True, output=info)
            
        elif invocation.tool_name == "get_capabilities":
            caps = [cap.describe().name for cap in self._registry.list_capabilities()]
            return ExecutionResult(success=True, output=f"Available Capabilities: {', '.join(caps)}")
            
        return ExecutionResult(success=False, error="Execution failed", output=None)

    def cancel(self, invocation_id: str) -> None:
        pass
