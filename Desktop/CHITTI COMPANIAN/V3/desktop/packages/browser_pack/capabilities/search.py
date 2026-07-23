from dataclasses import dataclass
from desktop.packages.browser_pack.strategies.search import SearchStrategy, DefaultSearchStrategy
from desktop.packages.browser_pack.models.semantic import SearchResults
from desktop.models.environment import EnvironmentContext

@dataclass
class CapabilityMetadata:
    requires_browser: bool = True
    supports_streaming: bool = False
    supports_presentation: bool = False
    supports_replay: bool = True
    supports_background: bool = True
    requires_login: bool = False
    produces_artifacts: bool = False

class SearchWebCapability:
    """
    Decides WHAT to do. Uses SearchStrategy for HOW to do it.
    """
    def __init__(self, strategy: SearchStrategy = None):
        self.strategy = strategy or DefaultSearchStrategy()
        self.metadata = CapabilityMetadata(supports_streaming=True, supports_presentation=True)

    def execute(self, query: str, context: EnvironmentContext) -> SearchResults:
        print(f"[SearchWebCapability] Initiating search for: {query}")
        # Dispatches to strategy which converts to atomic EnvironmentActions
        results = self.strategy.execute_search(query, context)
        return SearchResults(query=query, results=results)
