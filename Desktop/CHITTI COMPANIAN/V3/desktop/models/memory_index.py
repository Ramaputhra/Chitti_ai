from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from desktop.models.memory import Episode, Fact

class IMemoryIndex(ABC):
    """
    Abstract interface for all memory search providers.
    """
    
    @abstractmethod
    def index_episode(self, episode: Episode) -> bool:
        pass

    @abstractmethod
    def search_episodes(self, query: str, limit: int = 5) -> List[Episode]:
        pass

    @abstractmethod
    def index_fact(self, fact: Fact) -> bool:
        pass

    @abstractmethod
    def search_facts(self, query: str, limit: int = 5) -> List[Fact]:
        pass

class MemoryIndexManager:
    """
    Manages the active memory index provider.
    """
    def __init__(self, provider: IMemoryIndex):
        self._provider = provider

    def set_provider(self, provider: IMemoryIndex):
        self._provider = provider

    @property
    def provider(self) -> IMemoryIndex:
        return self._provider
