import time
from typing import Optional
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.models.web_models import BrowserContext
from desktop.platform.browser.browser_adapter import IBrowserAdapter

class SysBrowserLaunchAdapter:
    """
    Physical implementation for 'sys.browser.launch'.
    """
    
    def execute(
        self, 
        adapter: IBrowserAdapter, 
        browser_type: str = "chrome", 
        headless: bool = True,
        profile: Optional[str] = None
    ) -> ExecutionResult:
        try:
            session = adapter.launch(browser_type=browser_type, headless=headless, profile=profile)
            
            # Create the initial context containing the session and the first active tab
            active_tab = next((t for t in session.tabs if t.active), None)
            if not active_tab and session.tabs:
                active_tab = session.tabs[0]
                
            context = BrowserContext(session=session, tab=active_tab)
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"context": context}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                error_message=str(e)
            )
