from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.models.web_models import BrowserContext
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserWaitAdapter:
    """
    Physical implementation for 'sys.browser.wait'.
    Deterministic condition waiting (No LLM).
    """
    
    def execute(
        self, 
        adapter: IBrowserAdapter, 
        context: BrowserContext, 
        condition: str,
        selector: str = None,
        value: str = None,
        timeout_ms: int = 5000
    ) -> ExecutionResult:
        
        valid_conditions = [
            "element_visible", "element_hidden", "url_matches", "title_matches", 
            "network_idle", "document_ready", "download_completed", "dialog_open", "dialog_closed"
        ]
        
        if condition not in valid_conditions:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.INVALID_PARAMETER,
                error_message=f"Condition must be one of {valid_conditions}"
            )
            
        try:
            # Delegate strictly to adapter
            # Note: Adapter interface would be expanded to support condition-based wait
            success = adapter.wait(context, selector, timeout_ms)
            
            if success:
                return ExecutionResult(status=ExecutionStatus.SUCCESS)
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_code=ExecutionErrorCode.TIMEOUT,
                    error_message=f"Wait condition '{condition}' timed out after {timeout_ms}ms"
                )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                error_message=str(e)
            )
