from abc import ABC, abstractmethod
from desktop.models.retrieval import RetrievalQuery, RetrievalResult

class IRetrievalProvider(ABC):
    """
    Rule 287: Retrieval providers never rank globally.
    Rule 291: Retrieval is explainable (provider trace).
    Rule 292: Provider independence.
    """
    
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @abstractmethod
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        pass

class VectorRetrievalProvider(IRetrievalProvider):
    """Interface stub for future vector database integration."""
    def provider_id(self) -> str: return "provider.retrieval.vector"
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        raise NotImplementedError("Vector retrieval requires embeddings pipeline.")

class GraphRetrievalProvider(IRetrievalProvider):
    """Interface stub for future graph database traversal."""
    def provider_id(self) -> str: return "provider.retrieval.graph"
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        raise NotImplementedError("Graph retrieval requires graph DB integration.")

class InternetRetrievalProvider(IRetrievalProvider):
    """Interface stub for future search engine integration."""
    def provider_id(self) -> str: return "provider.retrieval.internet"
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        raise NotImplementedError("Internet retrieval not implemented.")

class PluginRetrievalProvider(IRetrievalProvider):
    """Interface stub for retrieving context from a 3rd party plugin."""
    def provider_id(self) -> str: return "provider.retrieval.plugin"
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        raise NotImplementedError("Plugin retrieval not implemented.")
