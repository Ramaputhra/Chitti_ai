import logging
from typing import Dict, Any

from desktop.models.component_states import HealthState, LifecycleState
from desktop.platform.components.registry import ProviderRegistry
from desktop.platform.components.loader import ManifestLoader
from desktop.platform.components.adapter import ProviderAdapter

logger = logging.getLogger(__name__)

class ComponentRuntime:
    """
    The master orchestrator for all component infrastructure.
    Responsible for component lifecycles, health checks, state transitions,
    and delegating metadata storage to the ProviderRegistry.
    
    This runtime knows nothing about AI domains (Intent, Vision, etc).
    """
    def __init__(self, registry: ProviderRegistry, loader: ManifestLoader):
        self.registry = registry
        self.loader = loader
        
        # Maps component_id to an instantiated ProviderAdapter
        self._adapters: Dict[str, ProviderAdapter] = {}
        # Maps component_id to its current physical lifecycle state
        self._lifecycle_states: Dict[str, LifecycleState] = {}
        
    def discover_components(self, manifests_dir: str) -> None:
        """
        Scan a directory for YAML manifests, load them, and register them.
        """
        import os
        if not os.path.exists(manifests_dir):
            return
            
        for filename in os.listdir(manifests_dir):
            if filename.endswith(('.yaml', '.yml')):
                filepath = os.path.join(manifests_dir, filename)
                manifest = self.loader.load_from_file(filepath)
                if manifest:
                    self.registry.register(manifest)
                    self._lifecycle_states[manifest.component_id] = LifecycleState.REGISTERED
                    logger.info(f"Registered component: {manifest.component_id}")

    def load_component(self, component_id: str, adapter: ProviderAdapter) -> bool:
        """
        Bind a concrete ProviderAdapter to a registered component_id and initialize it.
        """
        manifest = self.registry.find_by_id(component_id)
        if not manifest:
            logger.error(f"Cannot load unknown component: {component_id}")
            return False
            
        self._adapters[component_id] = adapter
        try:
            adapter.initialize()
            self._lifecycle_states[component_id] = LifecycleState.LOADED
            return True
        except Exception as e:
            logger.error(f"Failed to load component {component_id}: {e}")
            self._lifecycle_states[component_id] = LifecycleState.UNLOADED
            return False

    def warm_component(self, component_id: str) -> bool:
        """
        Pre-warm a loaded component (e.g., move weights to VRAM).
        """
        adapter = self._adapters.get(component_id)
        if not adapter:
            return False
            
        try:
            adapter.warm()
            self._lifecycle_states[component_id] = LifecycleState.WARM
            return True
        except Exception as e:
            logger.error(f"Failed to warm component {component_id}: {e}")
            return False

    def unload_component(self, component_id: str) -> None:
        """
        Unload a component, freeing up memory/VRAM.
        """
        adapter = self._adapters.get(component_id)
        if adapter:
            adapter.unload()
            self._lifecycle_states[component_id] = LifecycleState.UNLOADED
            # Remove adapter binding, but keep registry manifest
            del self._adapters[component_id]

    def check_health(self, component_id: str) -> HealthState:
        """
        Query the active health state of the component's adapter.
        """
        if self._lifecycle_states.get(component_id) == LifecycleState.REGISTERED:
            # Manifest known, but adapter not loaded yet
            return HealthState.OFFLINE
            
        adapter = self._adapters.get(component_id)
        if not adapter:
            return HealthState.UNKNOWN
            
        return adapter.health_check()
        
    def get_adapter(self, component_id: str) -> ProviderAdapter:
        """
        Retrieve the bound adapter for execution. 
        Note: The actual execution command `execute()` should be invoked 
        by the caller using this adapter reference.
        """
        return self._adapters.get(component_id)
