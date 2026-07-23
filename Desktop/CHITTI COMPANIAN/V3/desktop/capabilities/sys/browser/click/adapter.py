from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.models.web_models import BrowserContext
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserClickAdapter:
    """
    Physical implementation for 'sys.browser.click'.
    Depends on locate and wait implicitly via the browser adapter.
    """
    def execute(self, adapter: IBrowserAdapter, context: BrowserContext, selector: str, button: str = "left", modifiers: list = None, force: bool = False) -> ExecutionResult:
        try:
            # The adapter handles the actual click action, leveraging playwright.
            success = adapter.click(context, selector)
            
            if success:
                return ExecutionResult(status=ExecutionStatus.SUCCESS)
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                    error_message=f"Failed to click element: {selector}"
                )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
