from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.models.web_models import BrowserContext
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserTypeAdapter:
    def execute(self, adapter: IBrowserAdapter, context: BrowserContext, selector: str, text: str, delay_ms: int = 0, clear_first: bool = True) -> ExecutionResult:
        try:
            success = adapter.fill(context, selector, text)
            if success:
                return ExecutionResult(status=ExecutionStatus.SUCCESS)
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_message=f"Failed to type into element: {selector}"
                )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
