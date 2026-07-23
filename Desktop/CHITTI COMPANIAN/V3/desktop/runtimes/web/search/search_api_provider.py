from typing import Optional
from desktop.models.web_models import WebCollection, WebResourceType
from desktop.runtimes.web.search.isearch_provider import ISearchProvider

class SearchAPIProvider(ISearchProvider):
    @property
    def priority(self) -> int:
        return 1
        
    def search(self, query: str, limit: int = 10) -> Optional[WebCollection]:
        # Stub: calls a clean API like Bing/Google SERP API
        return WebCollection(
            resource_type=WebResourceType.SEARCH_RESULT.value,
            results=[],
            count=0
        )
