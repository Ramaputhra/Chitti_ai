import os
from typing import List

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.runtimes.capability.base import BaseCapability

class AppLauncherCapability(BaseCapability):
    """
    Launches applications, opens files or folders using the default Windows handler.
    """
    def __init__(self):
        super().__init__()
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "AppLauncherCapability"

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
            name="app_launcher",
            version="1.0",
            category="desktop",
            permissions=["filesystem", "desktop_control"],
            tools=self.discover_tools(),
            health="healthy",
            platform="windows"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="open_application",
                description="Launch an application or open a file/folder.",
                parameters=[
                    ToolParameter(name="path_or_name", type="string", description="The absolute path to the file/folder or the name of the executable (e.g. 'notepad').", required=True)
                ]
            )
        ]

    def execute(self, *args, **kwargs) -> ExecutionResult:
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            invocation = ToolInvocation(tool_name=action, parameters=parameters)

        if invocation.tool_name == "open_application":
            path_or_name = invocation.parameters.get("path_or_name", "")
            if not path_or_name:
                return ExecutionResult(success=False, error="path_or_name is required.")
                
            try:
                # os.startfile opens the file/app with its associated program
                if hasattr(os, "startfile"):
                    os.startfile(path_or_name)
                    return ExecutionResult(success=True, output=f"Opened {path_or_name}.")
                else:
                    return ExecutionResult(success=False, error="os.startfile is only available on Windows.")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
                
        return ExecutionResult(success=False, error=f"Unknown tool: {invocation.tool_name}")
