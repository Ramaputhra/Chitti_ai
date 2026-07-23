from abc import ABC, abstractmethod
from typing import List
from desktop.packages.browser_pack.models.semantic import SearchResult
from desktop.models.environment import EnvironmentContext

class SearchStrategy(ABC):
    @abstractmethod
    def execute_search(self, query: str, context: EnvironmentContext) -> List[SearchResult]:
        pass

class SearchEngineStrategy(SearchStrategy):
    def __init__(self, engine_url: str):
        self.engine_url = engine_url

    def execute_search(self, query: str, context: EnvironmentContext) -> List[SearchResult]:
        # Translates to NAVIGATE, INPUT_TEXT, SUBMIT, READ_RESOURCE, then parses results
        return [
            SearchResult(title="Example", url="https://example.com", snippet="...", source=self.engine_url, confidence=0.9)
        ]

class DefaultSearchStrategy(SearchStrategy):
    def __init__(self):
        self.strategy = SearchEngineStrategy("https://google.com")
        
    def execute_search(self, query: str, context: EnvironmentContext) -> List[SearchResult]:
        return self.strategy.execute_search(query, context)
