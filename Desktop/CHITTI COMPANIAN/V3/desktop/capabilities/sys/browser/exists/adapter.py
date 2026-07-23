from desktop.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.web_models import BrowserContext
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserExistsAdapter:
    """
    Physical implementation for 'sys.browser.exists'.
    Returns FOUND, NOT_FOUND, or MULTIPLE.
    """
    def execute(self, adapter: IBrowserAdapter, context: BrowserContext, selector: str) -> ExecutionResult:
        try:
            # Stub implementation logic
            # In a real implementation:
            # count = context.page.locator(selector).count()
            count = 1
            
            if count == 0:
                result = "NOT_FOUND"
            elif count == 1:
                result = "FOUND"
            else:
                result = "MULTIPLE"
                
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"result": result, "count": count}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
