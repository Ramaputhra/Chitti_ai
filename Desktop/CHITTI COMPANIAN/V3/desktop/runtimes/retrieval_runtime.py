from typing import List, Dict
import asyncio
from desktop.models.retrieval import RetrievalQuery, RetrievalResult, ContextPackage
from desktop.models.retrieval_provider import IRetrievalProvider
from desktop.runtimes.retrieval.ranking_engine import RankingEngine
from desktop.runtimes.retrieval.context_builder import ContextBuilder
from desktop.runtimes.retrieval.retrieval_cache import RetrievalCache

class RetrievalRuntime:
    """
    Orchestrates the entire Knowledge Retrieval Pipeline.
    Rule 286: Read-only.
    Rule 289: LLMs only query through this runtime.
    Rule 292: Provider independence (Runtime orchestrates).
    """
    def __init__(self, event_bus=None):
        self.providers: Dict[str, IRetrievalProvider] = {}
        self.ranking_engine = RankingEngine()
        self.context_builder = ContextBuilder()
        self.cache = RetrievalCache()
        self.event_bus = event_bus

    def register_provider(self, provider: IRetrievalProvider):
        self.providers[provider.provider_id()] = provider

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    async def retrieve_context(self, query: RetrievalQuery) -> ContextPackage:
        """
        The main entrypoint for the AI Gateway and Planner.
        Cache -> Providers -> Ranking -> ContextBuilder.
        """
        # 1. Cache Check
        cached_context = self.cache.get(query)
        if cached_context:
            self._emit("RetrievalCacheHit", {"query_intent": query.intent})
            return cached_context
            
        self._emit("RetrievalStarted", {"query_intent": query.intent})

        # 2. Parallel Provider Retrieval
        tasks = []
        for provider in self.providers.values():
            # In a real system, we'd filter providers based on query.namespaces 
            # and query.strategy (e.g., skip vector DB if strategy is GRAPH_ONLY).
            tasks.append(provider.retrieve(query))
            
        provider_results: List[RetrievalResult] = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = [r for r in provider_results if isinstance(r, RetrievalResult)]

        # 3. Global Ranking Engine
        # Rule 287: Global ranking belongs exclusively to Ranking Engine.
        ranked_result = self.ranking_engine.rank_and_merge(valid_results, query.token_budget)

        # 4. Context Builder
        # Rule 288: Context packages are immutable.
        context_package = self.context_builder.build(ranked_result)
        
        # 5. Cache and return
        self.cache.set(query, context_package)
        self._emit("RetrievalCompleted", {"query_intent": query.intent, "latency_ms": ranked_result.latency_ms})
        
        return context_package
