from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from desktop.models.web_models import BrowserSession, BrowserContext

class IBrowserAdapter(ABC):
    """
    Abstract interface for all browser backends (Playwright, Selenium, CDP).
    Capabilities never depend on the implementation, only this interface.
    """
    
    @abstractmethod
    def launch(self, browser_type: str, headless: bool = True, profile: Optional[str] = None) -> BrowserSession:
        pass
        
    @abstractmethod
    def navigate(self, context: BrowserContext, url: str) -> bool:
        pass
        
    @abstractmethod
    def click(self, context: BrowserContext, selector: str) -> bool:
        pass
        
    @abstractmethod
    def fill(self, context: BrowserContext, selector: str, text: str) -> bool:
        pass
        
    @abstractmethod
    def wait(self, context: BrowserContext, selector: str, timeout_ms: int = 5000) -> bool:
        pass
        
    @abstractmethod
    def scroll(self, context: BrowserContext, direction: str, amount: int) -> bool:
        pass
        
    @abstractmethod
    def download(self, context: BrowserContext, url: str, destination: str) -> bool:
        pass
        
    @abstractmethod
    def upload(self, context: BrowserContext, selector: str, file_path: str) -> bool:
        pass
        
    @abstractmethod
    def close(self, session: BrowserSession) -> bool:
        pass
        
    @abstractmethod
    def new_tab(self, session: BrowserSession) -> str:
        """Returns the ID of the new tab."""
        pass
        
    @abstractmethod
    def close_tab(self, context: BrowserContext) -> bool:
        pass
        
    @abstractmethod
    def switch_tab(self, context: BrowserContext) -> bool:
        pass
        
    @abstractmethod
    def back(self, context: BrowserContext) -> bool:
        pass
        
    @abstractmethod
    def forward(self, context: BrowserContext) -> bool:
        pass
        
    @abstractmethod
    def refresh(self, context: BrowserContext) -> bool:
        pass
