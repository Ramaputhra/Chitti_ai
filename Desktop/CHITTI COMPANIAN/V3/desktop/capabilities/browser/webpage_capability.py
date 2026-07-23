from typing import List, Dict, Any
import json

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.runtimes.capability.base import BaseCapability
from desktop.runtimes.browser.browser_manager import BrowserManager
from desktop.runtimes.browser.models import PageData

class WebPageCapability(BaseCapability):
    """
    Reads and extracts content from web pages using the Browser Runtime.
    """
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "WebPageCapability"

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
            name="web_page",
            version="1.0",
            category="web",
            permissions=["network"],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="read_page",
                description="Navigates to a URL and returns the text content of the page.",
                parameters=[
                    ToolParameter(name="url", type="string", description="The URL to read.", required=True)
                ]
            ),
            ToolDescriptor(
                name="extract_structured_data",
                description="Navigates to a URL and extracts structured data (links, tables, lists, headings).",
                parameters=[
                    ToolParameter(name="url", type="string", description="The URL to read.", required=True)
                ]
            )
        ]

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        url = invocation.parameters.get("url", "")
        if not url:
            return ExecutionResult(success=False, error="URL is required.")
            
        try:
            page_data: PageData = self.browser_manager.read_page(url)
            
            if invocation.tool_name == "read_page":
                return ExecutionResult(
                    success=True,
                    output=page_data.text_content
                )
            elif invocation.tool_name == "extract_structured_data":
                data = {
                    "title": page_data.title,
                    "headings": page_data.headings,
                    "links": page_data.links,
                    "code_blocks": page_data.code_blocks
                }
                return ExecutionResult(
                    success=True,
                    output=json.dumps(data, indent=2)
                )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
            
        return ExecutionResult(success=False, error=f"Unknown tool: {invocation.tool_name}")
