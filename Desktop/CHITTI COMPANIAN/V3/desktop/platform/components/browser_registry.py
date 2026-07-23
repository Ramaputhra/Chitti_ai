from typing import Dict, Any, List

class BrowserRegistry:
    """
    Registry for managing available browsers and their capabilities.
    The planner never hardcodes specific browsers like 'Chrome'; 
    it leverages this registry to understand what is available and what it can do.
    """
    
    def __init__(self):
        # In a real environment, this would dynamically discover installed browsers.
        # For the architecture, we register the known adapters.
        self.browsers = {
            "chrome": {
                "name": "Google Chrome",
                "supports_downloads": True,
                "supports_uploads": True,
                "supports_headless": True,
                "supports_extensions": True,
                "supports_profiles": True,
                "supports_incognito": True,
                "supports_pdf": True,
                "supports_devtools": True,
                "adapter": "playwright" # or CDP, Selenium
            },
            "edge": {
                "name": "Microsoft Edge",
                "supports_downloads": True,
                "supports_uploads": True,
                "supports_headless": True,
                "supports_extensions": True,
                "supports_profiles": True,
                "supports_incognito": True,
                "supports_pdf": True,
                "supports_devtools": True,
                "adapter": "playwright"
            },
            "firefox": {
                "name": "Mozilla Firefox",
                "supports_downloads": True,
                "supports_uploads": True,
                "supports_headless": True,
                "supports_extensions": True,
                "supports_profiles": True,
                "supports_incognito": True,
                "supports_pdf": True,
                "supports_devtools": True,
                "adapter": "playwright"
            }
        }
        self.default_browser = "chrome"
        
    def get_browser_capabilities(self, browser_id: str) -> Dict[str, Any]:
        return self.browsers.get(browser_id, {})
        
    def get_default_browser(self) -> str:
        return self.default_browser
        
    def get_all_browsers(self) -> List[str]:
        return list(self.browsers.keys())
