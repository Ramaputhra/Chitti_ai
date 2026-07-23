from typing import Dict, List, Optional
from desktop.platform.providers.base import BaseProvider

class ProviderRegistry:
    """
    Registry for storing and discovering providers organized by category.
    """
    def __init__(self):
        self._providers: Dict[str, Dict[str, BaseProvider]] = {}

    def register_provider(self, provider: BaseProvider) -> None:
        cat = provider.category.lower()
        pid = provider.provider_id.lower()
        if cat not in self._providers:
            self._providers[cat] = {}
        self._providers[cat][pid] = provider
        print(f"[ProviderRegistry] Registered provider '{pid}' under category '{cat}'")

    def get_provider(self, category: str, provider_id: str) -> Optional[BaseProvider]:
        cat_dict = self._providers.get(category.lower(), {})
        return cat_dict.get(provider_id.lower())

    def list_providers(self, category: str) -> List[BaseProvider]:
        cat_dict = self._providers.get(category.lower(), {})
        return list(cat_dict.values())
