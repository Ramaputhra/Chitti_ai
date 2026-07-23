from typing import List, Dict
from desktop.runtimes.web.iweb_runtime import IWebRuntime
from desktop.models.web_models import WebExecutionMode, BrowserContext
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode

class WebRuntime:
    """
    The orchestrator that routes capability execution to the appropriate IWebRuntime
    based on the policy decision.
    """
    
    def __init__(self, runtimes: List[IWebRuntime]):
        self._runtimes: Dict[WebExecutionMode, IWebRuntime] = {
            rt.supports_mode(): rt for rt in runtimes
        }
        
    def execute(
        self, 
        mode: WebExecutionMode, 
        capability_id: str, 
        context: BrowserContext, 
        **kwargs
    ) -> ExecutionResult:
        
        runtime = self._runtimes.get(mode)
        if not runtime:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                error_message=f"No runtime configured for mode {mode}"
            )
            
        # Delegate execution to the specific runtime implementation
        return runtime.execute_capability(capability_id, context, **kwargs)
