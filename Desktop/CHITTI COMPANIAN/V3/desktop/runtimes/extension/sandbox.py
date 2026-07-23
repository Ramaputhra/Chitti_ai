from desktop.models.plugin import PluginManifest, PluginContext
from desktop.platform.api import PlatformAPI
import logging

class PluginSandbox:
    """
    Logical interface sandbox for Sprint 8.4.
    Rule 279: Plugins receive NO direct references to core runtimes.
    They only interact with the PlatformAPI.
    """
    def __init__(self, manifest: PluginManifest, platform_api: PlatformAPI):
        self.manifest = manifest
        self.platform_api = platform_api
        self.is_loaded = False
        self._plugin_module = None

    def load_plugin(self, module_path: str):
        """
        Dynamically imports the plugin code. In the logical sandbox phase,
        this happens in the same process, but it provides only the PlatformAPI.
        """
        try:
            # Stub: importlib.import_module(module_path)
            # Ensure the plugin exposes an entry point that takes (PlatformAPI, PluginContext)
            self.is_loaded = True
            logging.info(f"Plugin {self.manifest.plugin_id} loaded into Logical Sandbox.")
        except Exception as e:
            logging.error(f"Failed to load plugin {self.manifest.plugin_id}: {e}")
            self.is_loaded = False

    def execute_capability(self, capability_id: str, request: dict, context: PluginContext) -> dict:
        """
        Rule 285: Context is passed in on every invocation, enforcing statelessness.
        """
        if not self.is_loaded:
            raise RuntimeError("Sandbox is not loaded.")
        
        # Stub: dispatch to internal module
        logging.info(f"Executing {capability_id} in sandbox for {self.manifest.plugin_id}")
        return {"status": "success", "result": f"Executed logically by {capability_id}"}
