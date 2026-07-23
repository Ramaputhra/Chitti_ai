from abc import ABC, abstractmethod
from typing import Optional
from desktop.models.web_models import WebCollection

class ISearchProvider(ABC):
    """
    Interface for search providers (API, Scraper, Headless) used by the SearchRuntime.
    """
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> Optional[WebCollection]:
        pass
        
    @property
    @abstractmethod
    def priority(self) -> int:
        """Lower number = higher priority. 1=API, 2=Scraper, 3=Headless"""
        pass
