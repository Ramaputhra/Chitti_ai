from desktop.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.web_models import BrowserContext
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserHoverAdapter:
    def execute(self, adapter: IBrowserAdapter, context: BrowserContext, selector: str) -> ExecutionResult:
        try:
            # Stub
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
        except Exception as e:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message=str(e))
