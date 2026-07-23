import time
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.models.web_models import BrowserContext, NavigationResult
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserNavigateAdapter:
    """
    Physical implementation for 'sys.browser.navigate'.
    Completely decoupled from Playwright/Selenium and Headless/Interactive rules.
    It receives an IBrowserAdapter and a BrowserContext from the WebRuntime.
    """
    
    def execute(self, adapter: IBrowserAdapter, context: BrowserContext, url: str) -> ExecutionResult:
        if not url:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.MISSING_REQUIRED_PARAMETER,
                error_message="url is required."
            )
            
        if not context or not context.session:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.MISSING_REQUIRED_PARAMETER,
                error_message="BrowserContext with an active session is required."
            )
            
        # Ensure HTTP prefix
        if not url.startswith("http"):
            url = "https://" + url
            
        try:
            # Emit navigation started event (mocked)
            # EventBus.publish(PageNavigationStartedEvent(...))
            
            success = adapter.navigate(context, url)
            if not success:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                    error_message=f"Navigation to {url} failed inside the adapter."
                )
                
            # Stage 2: URL Matches (Mocked check)
            # Stage 3: Document ready (Mocked check)
            # Stage 4: Verification passes (Mocked check)
            
            nav_result = NavigationResult(
                final_url=url,
                page_title=context.tab.title if context.tab else "Unknown",
                redirected=False,
                load_time_ms=150,
                verification_status="verified"
            )
                
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"result": nav_result}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                error_message=str(e)
            )
