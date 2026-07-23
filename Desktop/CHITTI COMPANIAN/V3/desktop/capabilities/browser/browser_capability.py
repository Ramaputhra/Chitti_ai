from typing import List, Dict, Any

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.capabilities.sys.browser.shared.browser_manager import BrowserManager

class BrowserCapability(ICapability):
    """
    Directly controls the managed Browser Session.
    """
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "BrowserCapability"

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
            name="browser_control",
            version="1.0",
            category="web",
            permissions=["desktop_control", "network"],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="browser_open_url",
                description="Navigates the managed browser to a URL.",
                parameters=[
                    ToolParameter(name="url", type="string", description="The URL.", required=True)
                ]
            )
        ]

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if invocation.tool_name == "browser_open_url":
            url = invocation.parameters.get("url", "")
            try:
                self.browser_manager.read_page(url)
                return ExecutionResult(success=True, output=f"Navigated to {url}.")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
                
        return ExecutionResult(success=False, error=f"Unknown tool: {invocation.tool_name}")
