from typing import Dict, Any
from desktop.models.environment import AdapterManifest

class AdapterRegistry:
    """
    Maintains the list of active adapters.
    Adapters are discovered through the ServiceRegistry/PackageManager, NOT by scanning folders (Rule 348).
    """
    def __init__(self):
        self._adapters: Dict[str, Any] = {}
        self._manifests: Dict[str, AdapterManifest] = {}

    def register_adapter(self, adapter_id: str, adapter_instance: Any, manifest: AdapterManifest):
        self._adapters[adapter_id] = adapter_instance
        self._manifests[adapter_id] = manifest
        print(f"[AdapterRegistry] Registered adapter {adapter_id} with capabilities {manifest.capabilities}")
