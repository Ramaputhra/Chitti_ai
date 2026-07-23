from typing import Optional
from desktop.models.web_models import WebCollection, WebResourceType
from desktop.runtimes.web.search.isearch_provider import ISearchProvider

class HeadlessSearchProvider(ISearchProvider):
    @property
    def priority(self) -> int:
        return 3
        
    def search(self, query: str, limit: int = 10) -> Optional[WebCollection]:
        # Stub: spins up headless playwright to bypass JS-challenges
        return WebCollection(
            resource_type=WebResourceType.SEARCH_RESULT.value,
            results=[],
            count=0
        )
