from typing import List, Dict, Any
import json
import urllib.parse

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.runtimes.capability.base import BaseCapability
from desktop.runtimes.browser.browser_manager import BrowserManager
from desktop.runtimes.browser.models import SearchResult, PageData

class BrowserResearchCapability(BaseCapability):
    """
    Flagship capability for end-to-end web research.
    Broken down into discrete stages: Search -> Filter -> Extract -> Validate.
    """
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "BrowserResearchCapability"

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
            name="browser_research",
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
                name="search",
                description="Searches the web for a query.",
                parameters=[ToolParameter(name="query", type="string", description="The search query.", required=True)]
            ),
            ToolDescriptor(
                name="filter_sources",
                description="Filters and ranks search results (deterministic).",
                parameters=[ToolParameter(name="results", type="array", description="List of search result dicts.", required=True)]
            ),
            ToolDescriptor(
                name="extract_content",
                description="Extracts content from a list of sources.",
                parameters=[ToolParameter(name="sources", type="array", description="List of selected sources.", required=True)]
            ),
            ToolDescriptor(
                name="validate_evidence",
                description="Validates extracted content (removes empty, paywalls, etc).",
                parameters=[ToolParameter(name="documents", type="array", description="List of extracted documents.", required=True)]
            )
        ]

    def execute(self, *args, **kwargs) -> ExecutionResult:
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            invocation = ToolInvocation(tool_name=action, parameters=parameters)
            
        try:
            if invocation.tool_name == "search":
                return self._search(invocation.parameters)
            elif invocation.tool_name == "filter_sources":
                return self._filter_sources(invocation.parameters)
            elif invocation.tool_name == "extract_content":
                return self._extract_content(invocation.parameters)
            elif invocation.tool_name == "validate_evidence":
                return self._validate_evidence(invocation.parameters)
            else:
                return ExecutionResult(success=False, error=f"Unknown tool: {invocation.tool_name}")
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))

    def _search(self, parameters: Dict[str, Any]) -> ExecutionResult:
        query = parameters.get("query", "")
        if not query:
            return ExecutionResult(success=False, error="query is required")
            
        results: List[SearchResult] = self.browser_manager.search(query)
        # Convert objects to dicts for state passing
        res_dicts = [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in results]
        
        return ExecutionResult(
            success=True, 
            output="Search completed.", 
            data={"results": res_dicts}
        )

    def _filter_sources(self, parameters: Dict[str, Any]) -> ExecutionResult:
        results = parameters.get("results", [])
        if not results:
            return ExecutionResult(success=False, error="results is required")
            
        # Stage 1: Deterministic filter (dedupe, remove blacklisted domains)
        blacklist = ["pinterest.com", "facebook.com", "instagram.com"]
        seen_domains = set()
        selected = []
        
        for r in results:
            url = r.get("url", "")
            try:
                domain = urllib.parse.urlparse(url).netloc.lower()
            except:
                continue
                
            if any(b in domain for b in blacklist):
                continue
            if domain in seen_domains:
                continue
                
            seen_domains.add(domain)
            selected.append(r)
            if len(selected) >= 3: # Keep top 3 distinct domains
                break
                
        return ExecutionResult(
            success=True,
            output=f"Filtered down to {len(selected)} sources.",
            data={"sources": selected}
        )

    def _extract_content(self, parameters: Dict[str, Any]) -> ExecutionResult:
        sources = parameters.get("sources", [])
        if not sources:
            return ExecutionResult(success=False, error="sources is required")
            
        documents = []
        for src in sources:
            url = src.get("url")
            try:
                page_data: PageData = self.browser_manager.read_page(url)
                documents.append({
                    "url": url,
                    "title": src.get("title", ""),
                    "content": page_data.text_content,
                    "status": "success"
                })
            except Exception as e:
                documents.append({
                    "url": url,
                    "title": src.get("title", ""),
                    "content": "",
                    "status": "failed",
                    "error": str(e)
                })
                
        return ExecutionResult(
            success=True,
            output=f"Extracted {len(documents)} documents.",
            data={"documents": documents}
        )

    def _validate_evidence(self, parameters: Dict[str, Any]) -> ExecutionResult:
        documents = parameters.get("documents", [])
        if not documents:
            return ExecutionResult(success=False, error="documents is required")
            
        verified = []
        for doc in documents:
            if doc.get("status") != "success":
                continue
            
            content = doc.get("content", "").strip()
            
            # Reject empty or very short
            if len(content) < 100:
                continue
                
            # Reject likely paywalls / captcha blockers
            lowered = content.lower()
            if "please verify you are a human" in lowered or "enable cookies" in lowered:
                continue
            if "subscribe to read" in lowered or "paywall" in lowered:
                continue
                
            verified.append(doc)
            
        return ExecutionResult(
            success=True,
            output=f"Validated {len(verified)} pieces of evidence.",
            data={"evidence": verified}
        )
