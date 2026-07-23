from typing import Any, Dict, List, Optional

from playwright.sync_api import Browser, Playwright, sync_playwright

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth


class PlaywrightProvider(IProvider):
    """
    Implements browser interaction via Playwright.
    Managed by the BrowserCapability.
    """
    def __init__(self, logger: ILoggingService, headless: bool = True):
        self.logger = logger
        self.headless = headless
        self._state = ServiceState.STOPPED
        self._is_healthy = False
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    @property
    def name(self) -> str: return "PlaywrightProvider"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing Playwright Provider...")
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self._is_healthy = True
            self._state = ServiceState.RUNNING
            self.logger.info("Playwright initialized successfully.")
        except Exception as e:
            self.logger.error(f"Playwright initialization failed: {e}")
            self._is_healthy = False

    def shutdown(self) -> None:
        self.logger.info("Shutting down Playwright Provider...")
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    def get_provider_health(self) -> ProviderHealth:
        return ProviderHealth(
            status="Healthy" if self._is_healthy else "Unavailable",
            healthy=self._is_healthy,
            enabled=True,
            configured=True,
            authenticated=True,
            latency_ms=1200,
            last_error=None,
            version="1.42.0",
            model="chromium",
            uptime=0
        )

    def health_check(self) -> Dict[str, Any]:
        h = self.get_provider_health()
        return {"status": h.status, "headless": self.headless}

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 1200} # Browser launch/navigation overhead

    def capabilities(self) -> List[str]:
        return ["navigate", "extract_dom", "screenshot", "click"]

    def version(self) -> str:
        return "1.42.0"

    def configuration(self) -> Dict[str, Any]:
        return {"headless": self.headless}

    def execute_intent(self, url: str, intent: str) -> Dict[str, Any]:
        if not self._is_healthy or not self.browser:
            return {"status": "failed", "reason": "Playwright unavailable"}
            
        self.logger.info(f"Playwright executing intent on {url}...")
        try:
            page = self.browser.new_page()
            page.goto(url)
            # In a real implementation, we would inject JS or use the intent to drive actions.
            # Here we just extract the page title for integration proof.
            title = page.title()
            page.close()
            return {"status": "success", "title": title}
        except Exception as e:
            self.logger.error(f"Playwright execution failed: {e}")
            return {"status": "failed", "reason": str(e)}
