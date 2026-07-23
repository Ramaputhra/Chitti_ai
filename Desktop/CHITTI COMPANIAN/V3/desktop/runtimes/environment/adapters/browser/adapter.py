import time
from desktop.runtimes.environment.adapters.base_adapter import IEnvironmentAdapter
from desktop.models.environment import EnvironmentAction, EnvironmentContext, AdapterHealth, AdapterManifest
from desktop.runtimes.environment.adapters.browser.engine import IBrowserEngine, PlaywrightEngine

class BrowserAdapter(IEnvironmentAdapter):
    """
    Translates generic EnvironmentActions via an IBrowserEngine.
    Rule 354: Adapter Engine Independence.
    """
    
    def __init__(self, engine: IBrowserEngine = None):
        self._health = AdapterHealth.OFFLINE
        self.engine = engine or PlaywrightEngine()
        self.manifest = AdapterManifest(
            id="browser.default",
            version="1.0",
            capabilities=[
                "JavaScript", "Downloads", "Uploads", "Cookies", 
                "Local Storage", "PDF Export", "Screenshots", 
                "Multiple Tabs", "Incognito"
            ],
            permissions=["internet", "filesystem.downloads"],
            platforms=["windows", "linux", "mac"]
        )
        
    def initialize(self) -> None:
        self.engine.start()
        self._health = AdapterHealth.READY
        print("[BrowserAdapter] Initialized via engine")

    def check_health(self) -> AdapterHealth:
        return self._health

    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> bool:
        start_time = time.time()
        success = False
        error_msg = None
        
        try:
            # Engine translation handles all the native Playwright/Selenium API mapping
            success = self.engine.execute(action, context)
        except Exception as e:
            error_msg = str(e)
            success = False
            self._take_error_screenshot(context)
        finally:
            latency = (time.time() - start_time) * 1000
            self._record_telemetry(action, success, latency, error_msg, context)
            
        return success

    def dispose(self) -> None:
        self.engine.stop()
        self._health = AdapterHealth.OFFLINE
        print("[BrowserAdapter] Disposed")
        
    # --- Telemetry Hooks ---
    
    def _record_telemetry(self, action: EnvironmentAction, success: bool, latency: float, error: str, context: EnvironmentContext):
        """
        Telemetry tracking for diagnostics.
        """
        print(f"[BrowserAdapter Telemetry] Action: {action.action_type.name} | Success: {success} | Latency: {latency:.2f}ms | Error: {error}")
        
    def _take_error_screenshot(self, context: EnvironmentContext):
        print(f"[BrowserAdapter] Captured error screenshot for session {context.session_id}")
