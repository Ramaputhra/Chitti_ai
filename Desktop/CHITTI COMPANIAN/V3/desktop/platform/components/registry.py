from typing import List, Dict, Optional
from desktop.models.component_manifest import ComponentManifest, CapabilityRequirements

class ProviderRegistry:
    """
    Central registry storing all typed ComponentManifest objects.
    Does NOT instantiate providers; only manages discovery and metadata.
    """
    def __init__(self):
        # Maps component_id to its manifest
        self._manifests: Dict[str, ComponentManifest] = {}
        # Maps capability name to a list of supporting component_ids
        self._capability_index: Dict[str, List[str]] = {}

    def register(self, manifest: ComponentManifest) -> None:
        """Register a new provider manifest."""
        self._manifests[manifest.component_id] = manifest
        
        for capability in manifest.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            if manifest.component_id not in self._capability_index[capability]:
                self._capability_index[capability].append(manifest.component_id)

    def unregister(self, component_id: str) -> None:
        """Remove a provider manifest by its ID."""
        manifest = self._manifests.pop(component_id, None)
        if manifest:
            for capability in manifest.capabilities:
                if capability in self._capability_index:
                    try:
                        self._capability_index[capability].remove(component_id)
                    except ValueError:
                        pass

    def find_by_id(self, component_id: str) -> Optional[ComponentManifest]:
        """Find a provider's manifest by its ID."""
        return self._manifests.get(component_id)

    def find_by_capability(self, capability: str) -> List[ComponentManifest]:
        """Find all provider manifests that support a specific capability."""
        component_ids = self._capability_index.get(capability, [])
        return [self._manifests[cid] for cid in component_ids if cid in self._manifests]

    def enumerate_providers(self) -> List[ComponentManifest]:
        """Return all registered providers."""
        return list(self._manifests.values())

    def validate_requirements(self, requirements: CapabilityRequirements) -> bool:
        """
        Check if the registry has components that satisfy all 'requires' capabilities.
        """
        for req in requirements.requires:
            if req not in self._capability_index or not self._capability_index[req]:
                return False
        return True
