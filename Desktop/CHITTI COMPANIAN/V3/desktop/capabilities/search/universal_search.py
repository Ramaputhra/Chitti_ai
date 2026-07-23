import asyncio
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.runtimes.capability.models import CapabilityDescriptor, CapabilityParameter, ExecutionResult
from desktop.runtimes.search.search_runtime import UniversalSearchRuntime
from desktop.runtimes.search.models import SearchQuery

class UniversalSearchCapability(ICapability):
    """
    Unified entry point for the Planner to search across all CHITTI domains.
    Delegates to the UniversalSearchRuntime.
    """
    def __init__(self, search_runtime: UniversalSearchRuntime, event_loop: asyncio.AbstractEventLoop):
        self.search_runtime = search_runtime
        self.loop = event_loop

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="UniversalSearchCapability",
            description="Searches across all observable domains in CHITTI (Files, Activity, Memory, etc.).",
            parameters=[
                CapabilityParameter(
                    name="query",
                    type="string",
                    description="The search terms or intent.",
                    required=True
                ),
                CapabilityParameter(
                    name="domains",
                    type="list",
                    description="List of domains to search (e.g., ['FILES', 'ACTIVITY']). Defaults to ALL.",
                    required=False
                )
            ]
        )

    def execute(self, action: str, parameters: dict, context, token) -> ExecutionResult:
        query_text = parameters.get("query")
        if not query_text:
            return ExecutionResult(success=False, error="query is required")
            
        domains = parameters.get("domains", ["ALL"])
        
        # Build the SearchQuery
        query = SearchQuery(
            text=query_text,
            domains=domains
        )
        
        # Dispatch to runtime asynchronously
        asyncio.run_coroutine_threadsafe(self.search_runtime.search(query), self.loop)
        
        # Return success immediately; presentation runtime handles the UI
        return ExecutionResult(success=True, output=f"Dispatched Universal Search for '{query_text}'")
