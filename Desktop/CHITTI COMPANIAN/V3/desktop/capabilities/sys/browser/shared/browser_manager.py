from typing import Optional, Dict
from desktop.platform.browser.browser_adapter import IBrowserAdapter
from desktop.platform.browser.playwright_adapter import PlaywrightAdapter
from desktop.platform.components.browser_registry import BrowserRegistry

class BrowserManager:
    """
    Manages the lifecycle and instantiation of browser adapters.
    Capabilities request an adapter from here, oblivious to the backend.
    """
    
    def __init__(self, registry: BrowserRegistry):
        self.registry = registry
        self._active_adapters: Dict[str, IBrowserAdapter] = {}
        
    def get_adapter(self, browser_id: Optional[str] = None) -> IBrowserAdapter:
        bid = browser_id or self.registry.get_default_browser()
        
        if bid not in self._active_adapters:
            # In a real environment, we would instantiate dynamically based on the registry.
            # Here we hardcode to PlaywrightAdapter for the architecture.
            self._active_adapters[bid] = PlaywrightAdapter()
            
        return self._active_adapters[bid]
