from typing import List, Type
from desktop.productivity.providers.base import ContextProvider

class ContextProviderRegistry:
    """
    Maintains a list of all active Context Providers.
    Rule 44: Providers are independent. EpisodeBuilder accesses them strictly through this registry.
    """
    _providers: List[ContextProvider] = []
    
    @classmethod
    def register(cls, provider: ContextProvider):
        cls._providers.append(provider)
        
    @classmethod
    def providers(cls) -> List[ContextProvider]:
        return cls._providers
