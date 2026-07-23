import logging
from typing import List, Optional, Dict, Any

from desktop.models.remote_provider import RemoteProviderManifest, ProviderState, RemoteRequest
from desktop.platform.ai.remote_registry import RemoteProviderRegistry

logger = logging.getLogger(__name__)

class ProviderSelector:
    """
    Responsible strictly for ranking and selecting the best healthy remote provider.
    Decoupled from the AdaptiveAIRouter to allow future optimization of ranking logic.
    """
    def __init__(self, registry: RemoteProviderRegistry):
        self.registry = registry

    def select_best_provider(self, request: RemoteRequest, excluded_providers: Optional[List[str]] = None) -> Optional[RemoteProviderManifest]:
        """
        Selects the best provider based on capabilities, priority, and health.
        """
        excluded = excluded_providers or []
        candidates = self.registry.get_all_providers()
        
        # 1. Filter out excluded
        candidates = [c for c in candidates if c.provider_id not in excluded]
        
        # 2. Filter by Capability Requirements
        # (This is simplified. In reality, the RemoteRequest would specify its required capabilities)
        if request.service == "vision":
            candidates = [c for c in candidates if c.capabilities.vision]
            
        # 3. Filter by known FAILED states (if tracking global states elsewhere)
        # Assuming the Provider Adapters handle transient state tracking internally via circuit breakers.
        
        # 4. Sort by priority
        candidates.sort(key=lambda c: c.priority, reverse=True)
        
        if not candidates:
            return None
            
        selected = candidates[0]
        logger.debug(f"ProviderSelector ranked {selected.provider_id} as the optimal provider for {request.service}.")
        return selected
