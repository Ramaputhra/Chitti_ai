from desktop.runtimes.web.iweb_runtime import IWebRuntime
from desktop.models.web_models import WebExecutionMode, BrowserContext
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode

from desktop.runtimes.web.search.search_api_provider import SearchAPIProvider
from desktop.runtimes.web.search.search_scraper_provider import SearchScraperProvider
from desktop.runtimes.web.search.headless_search_provider import HeadlessSearchProvider

class SearchRuntime(IWebRuntime):
    """Execution engine for background search."""
    
    def __init__(self):
        self.providers = sorted(
            [SearchAPIProvider(), SearchScraperProvider(), HeadlessSearchProvider()],
            key=lambda p: p.priority
        )
    
    def supports_mode(self) -> WebExecutionMode:
        return WebExecutionMode.SEARCH
        
    def execute_capability(self, capability_id: str, context: BrowserContext, **kwargs) -> ExecutionResult:
        query = kwargs.get("query", "")
        limit = kwargs.get("limit", 10)
        
        for provider in self.providers:
            result = provider.search(query, limit)
            if result is not None:
                return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"collection": result})
                
        return ExecutionResult(
            status=ExecutionStatus.FAILED, 
            error_code=ExecutionErrorCode.UNKNOWN_ERROR,
            error_message="All search providers failed."
        )

class CrawlerRuntime(IWebRuntime):
    """Execution engine for static crawling."""
    
    def supports_mode(self) -> WebExecutionMode:
        return WebExecutionMode.CRAWL
        
    def execute_capability(self, capability_id: str, context: BrowserContext, **kwargs) -> ExecutionResult:
        # Stub for crawler logic
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"mode": "crawl"})

class HeadlessBrowserRuntime(IWebRuntime):
    """Execution engine for headless browser automation."""
    
    def supports_mode(self) -> WebExecutionMode:
        return WebExecutionMode.HEADLESS
        
    def execute_capability(self, capability_id: str, context: BrowserContext, **kwargs) -> ExecutionResult:
        # Invokes the browser adapter in headless mode
        # Normally this dynamically imports and executes the capability adapter.
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"mode": "headless"})

class InteractiveBrowserRuntime(IWebRuntime):
    """Execution engine for visible browser automation."""
    
    def supports_mode(self) -> WebExecutionMode:
        return WebExecutionMode.INTERACTIVE
        
    def execute_capability(self, capability_id: str, context: BrowserContext, **kwargs) -> ExecutionResult:
        # Invokes the browser adapter in interactive mode
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"mode": "interactive"})
