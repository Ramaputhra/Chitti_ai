import logging
from typing import Dict, List, Optional
from desktop.models.remote_provider import RemoteProviderManifest

logger = logging.getLogger(__name__)

class RemoteProviderRegistry:
    """
    Acts as the catalog for available remote endpoints and models.
    """
    def __init__(self):
        self._providers: Dict[str, RemoteProviderManifest] = {}

    def register_provider(self, manifest: RemoteProviderManifest) -> None:
        """Registers a remote provider manifest."""
        self._providers[manifest.provider_id] = manifest
        logger.info(f"Registered remote provider: {manifest.provider_id}")

    def get_provider(self, provider_id: str) -> Optional[RemoteProviderManifest]:
        """Retrieves a provider manifest by its ID."""
        return self._providers.get(provider_id)

    def get_all_providers(self) -> List[RemoteProviderManifest]:
        """Returns all registered providers sorted by priority."""
        return sorted(list(self._providers.values()), key=lambda p: p.priority, reverse=True)

    def unregister_provider(self, provider_id: str) -> None:
        """Removes a provider from the registry."""
        if provider_id in self._providers:
            del self._providers[provider_id]
            logger.info(f"Unregistered remote provider: {provider_id}")
