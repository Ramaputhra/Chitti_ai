from desktop.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.web_models import BrowserContext
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserScrollAdapter:
    def execute(self, adapter: IBrowserAdapter, context: BrowserContext, direction: str, amount: int = 500, selector: str = None) -> ExecutionResult:
        try:
            success = adapter.scroll(context, direction, amount)
            if success:
                return ExecutionResult(status=ExecutionStatus.SUCCESS)
            else:
                return ExecutionResult(status=ExecutionStatus.FAILED, error_message="Scroll failed")
        except Exception as e:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message=str(e))
