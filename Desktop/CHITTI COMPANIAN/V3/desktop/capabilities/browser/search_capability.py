from typing import List, Dict, Any, Optional
import json

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.runtimes.capability.base import BaseCapability
from desktop.runtimes.browser.browser_manager import BrowserManager
from desktop.runtimes.browser.models import SearchResult

class SearchCapability(BaseCapability):
    """
    Allows CHITTI to search the web using the Browser Runtime.
    """
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SearchCapability"

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
            name="web_search",
            version="1.0",
            category="web",
            permissions=["network", "desktop_control"],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="search_web",
                description="Searches the web for a query and returns the top results.",
                parameters=[
                    ToolParameter(name="query", type="string", description="The search query.", required=True)
                ]
            ),
            ToolDescriptor(
                name="open_search_result",
                description="Opens a search result URL in the user's default browser.",
                parameters=[
                    ToolParameter(name="url", type="string", description="The URL to open.", required=True)
                ]
            )
        ]

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if invocation.tool_name == "search_web":
            query = invocation.parameters.get("query", "")
            try:
                results: List[SearchResult] = self.browser_manager.search(query)
                json_results = [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in results]
                return ExecutionResult(
                    success=True,
                    output=json.dumps(json_results, indent=2)
                )
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
                
        elif invocation.tool_name == "open_search_result":
            url = invocation.parameters.get("url", "")
            try:
                self.browser_manager.open_url_for_user(url)
                return ExecutionResult(success=True, output=f"Opened {url} in user's default browser.")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
                
        return ExecutionResult(success=False, error=f"Unknown tool: {invocation.tool_name}")
