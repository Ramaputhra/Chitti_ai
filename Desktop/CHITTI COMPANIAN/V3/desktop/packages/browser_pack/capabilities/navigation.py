import webbrowser
from typing import Dict, Any, Optional
from desktop.packages.sdk.pack_metadata import CapabilityMetadata
from desktop.platform.shared.models.execution import ExecutionResult, ExecutionStatus

class OpenBrowserCapability:
    """
    Opens a URL in the default system web browser.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(
            category="Browser",
            supports_undo=False
        )
        
    def execute(self, url: str) -> Dict[str, Any]:
        print(f"[OpenBrowserCapability] Opening URL: {url}")
        try:
            # Add http:// if missing, otherwise webbrowser might fail
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
                
            success = webbrowser.open(url)
            if success:
                return {"status": "opened", "url": url, "error": None}
            else:
                return {"status": "failed", "url": url, "error": "Failed to launch browser"}
        except Exception as e:
            print(f"[OpenBrowserCapability] Failed: {e}")
            return {"status": "error", "url": url, "error": str(e)}
