from typing import Callable, Any, List
from desktop.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.web_models import WebExecutionMode

class BrowserRecoveryRuntime:
    """
    Generic recovery pipeline that can escalate execution runtimes on failure.
    (e.g., HTTP_FETCH -> HEADLESS -> INTERACTIVE)
    """
    
    def __init__(self, escalation_path: List[WebExecutionMode] = None):
        self.escalation_path = escalation_path or [
            WebExecutionMode.HTTP_FETCH, 
            WebExecutionMode.HEADLESS, 
            WebExecutionMode.INTERACTIVE
        ]
        
    def execute_with_recovery(
        self, 
        action_func: Callable[[WebExecutionMode], ExecutionResult]
    ) -> ExecutionResult:
        
        last_result = None
        
        for mode in self.escalation_path:
            # 1. Recover/Refresh/Clear transient state before next attempt
            self._clear_transient_state()
            
            # 2. Attempt execution in current mode
            last_result = action_func(mode)
            
            if last_result.status == ExecutionStatus.SUCCESS:
                return last_result
                
            # If failed, it continues to the next mode in the escalation path (escalating runtime)
            
        return last_result # Return final failure after exhausting escalation path
        
    def _clear_transient_state(self):
        # Clears transient DOM state or resets adapters
        pass
