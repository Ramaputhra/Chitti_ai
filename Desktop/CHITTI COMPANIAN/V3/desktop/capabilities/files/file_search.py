import asyncio
from desktop.runtimes.capability.models import CapabilityDescriptor, CapabilityParameter, ExecutionResult
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.runtimes.search.search_runtime import UniversalSearchRuntime
from desktop.runtimes.search.models import SearchQuery

class FileSearchCapability(ICapability):
    """
    Capability to search for files on the local filesystem.
    Refactored to orchestrate via UniversalSearchRuntime with domains=[FILES].
    """
    def __init__(self, search_runtime: UniversalSearchRuntime, event_loop: asyncio.AbstractEventLoop):
        self.search_runtime = search_runtime
        self.loop = event_loop

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="FileSearchCapability",
            description="Searches for files by name matching the query.",
            parameters=[
                CapabilityParameter(
                    name="query",
                    type="string",
                    description="The filename or partial name to search for",
                    required=True
                ),
                CapabilityParameter(
                    name="directory",
                    type="string",
                    description="The root directory to search within (defaults to user home ~)",
                    required=False
                ),
                CapabilityParameter(
                    name="max_results",
                    type="integer",
                    description="Maximum number of results to return",
                    required=False
                )
            ]
        )

    def execute(self, action: str, parameters: dict, context, token) -> ExecutionResult:
        query_text = parameters.get("query")
        if not query_text:
            return ExecutionResult(success=False, error="query is required")
            
        directory = parameters.get("directory", "~")
        max_results = parameters.get("max_results", 10)
        
        # Build the SearchQuery
        query = SearchQuery(
            text=query_text,
            domains=["FILES"],
            limit=max_results,
            semantic_filters={"directory": directory}
        )
        
        # Dispatch to runtime asynchronously
        asyncio.run_coroutine_threadsafe(self.search_runtime.search(query), self.loop)
        
        # Return success immediately; presentation runtime handles the UI
        return ExecutionResult(success=True, output=f"Dispatched File Search for '{query_text}' via UniversalSearchRuntime.")
