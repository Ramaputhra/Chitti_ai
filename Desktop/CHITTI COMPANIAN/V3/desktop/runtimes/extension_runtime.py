import os
from typing import Dict, List
import logging
from desktop.models.plugin import PluginManifest, PluginLifecycle
from desktop.platform.api import PlatformAPI
from desktop.runtimes.extension.validator import PluginValidator, CompatibilityChecker
from desktop.runtimes.extension.sandbox import PluginSandbox
from desktop.runtimes.service_registry_runtime import ServiceRegistryRuntime

class ExtensionRuntime:
    """
    Orchestrates the entire Plugin Loading pipeline.
    Loader -> Validator -> Compatibility Checker -> Sandbox -> Registry
    Rule 280: Enforces resource limits.
    Rule 281: Event ownership strictly held by core runtimes.
    """
    def __init__(self, platform_api: PlatformAPI, service_registry: ServiceRegistryRuntime):
        self.platform_api = platform_api
        self.service_registry = service_registry
        self.validator = PluginValidator()
        # In a real app, this version comes from CHITTI_PLATFORM_SPEC or config
        self.compatibility_checker = CompatibilityChecker(current_platform_version="1.0.0")
        self.sandboxes: Dict[str, PluginSandbox] = {}
        
    def discover_plugins(self, plugins_dir: str):
        """Scans the directory for plugin packages."""
        if not os.path.exists(plugins_dir):
            return
            
        # Stub: iterate directories, parse plugin.yaml into PluginManifest objects
        # and then pass them to self.install_plugin(manifest, path)
        pass

    def install_plugin(self, manifest: PluginManifest, plugin_path: str) -> bool:
        """
        Executes the hot-loading lifecycle.
        DISCOVERED -> VERIFIED -> VALIDATED -> LOADED -> REGISTERED -> ENABLED
        """
        logging.info(f"Discovered plugin: {manifest.plugin_id}")
        
        # 1. Validate
        if not self.validator.validate(manifest):
            logging.error(f"Plugin {manifest.plugin_id} failed structural validation.")
            return False
            
        # 2. Check Compatibility
        if not self.compatibility_checker.check(manifest):
            logging.error(f"Plugin {manifest.plugin_id} failed compatibility check.")
            return False
            
        # 3. Create Sandbox
        sandbox = PluginSandbox(manifest, self.platform_api)
        sandbox.load_plugin(plugin_path)
        
        if not sandbox.is_loaded:
            return False
            
        self.sandboxes[manifest.plugin_id] = sandbox
        
        # 4. Inject into Service Registry
        # Plugins never touch the registry directly; the ExtensionRuntime does it on their behalf.
        # Stub: Parse the capabilities/providers provided by the plugin and inject their ServiceDescriptors
        # into self.service_registry
        
        logging.info(f"Plugin {manifest.plugin_id} successfully loaded and registered.")
        return True
