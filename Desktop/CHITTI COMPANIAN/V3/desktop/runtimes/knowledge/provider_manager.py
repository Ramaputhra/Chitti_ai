from typing import List, Dict
from desktop.models.knowledge_provider import IKnowledgeProvider, KnowledgeCollectionTrigger, KnowledgeCollectionResult

class ProviderManager:
    """
    Manages Knowledge Providers.
    Rule 272: Routes events/triggers to providers to pull knowledge deterministically.
    """
    def __init__(self):
        self._providers: Dict[str, IKnowledgeProvider] = {}

    def register_provider(self, provider: IKnowledgeProvider):
        desc = provider.descriptor()
        self._providers[desc.provider_id] = provider

    def get_providers_for_namespace(self, namespace) -> List[IKnowledgeProvider]:
        # Filter and sort by priority
        matched = [p for p in self._providers.values() if namespace in p.descriptor().namespaces]
        matched.sort(key=lambda p: p.descriptor().priority, reverse=True)
        return matched

    async def trigger_collection(self, trigger: KnowledgeCollectionTrigger) -> List[KnowledgeCollectionResult]:
        """
        Pulls data from all applicable providers based on the trigger event.
        """
        results = []
        for provider in self._providers.values():
            # In a real implementation, we would filter providers based on their RefreshPolicy
            # and whether this specific trigger applies to them.
            result = await provider.collect(trigger)
            results.append(result)
        return results
