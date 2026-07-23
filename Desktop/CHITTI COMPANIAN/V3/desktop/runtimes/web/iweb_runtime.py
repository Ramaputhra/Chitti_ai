from abc import ABC, abstractmethod
from desktop.models.web_models import WebExecutionMode, BrowserContext
from desktop.models.execution import ExecutionResult

class IWebRuntime(ABC):
    """
    Abstract interface for all web runtimes (Search, Crawl, Headless, Interactive).
    """
    
    @abstractmethod
    def supports_mode(self) -> WebExecutionMode:
        pass
        
    @abstractmethod
    def execute_capability(self, capability_id: str, context: BrowserContext, **kwargs) -> ExecutionResult:
        """
        Executes a browser capability using this specific runtime environment.
        """
        pass
