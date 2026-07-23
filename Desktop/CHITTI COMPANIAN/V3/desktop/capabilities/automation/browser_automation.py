import webbrowser
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from desktop.app.capability_contracts import ICapability, CapabilityDescriptor
from desktop.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus

class RestoreBrowserSessionCapability(ICapability):
    """
    Restores a previous browser session by opening a list of URLs with filtering support.
    """
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        urls = context.workflow.parameters.get("urls", [])
        browser = context.workflow.parameters.get("browser", "default")
        domain_filter = context.workflow.parameters.get("domain_filter", None)
        limit = context.workflow.parameters.get("limit", None)
        exclude_duplicates = context.workflow.parameters.get("exclude_duplicates", True)
        
        if not urls:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="No URLs provided to restore.")
            
        final_urls = []
        seen = set()
        
        for url in urls:
            if exclude_duplicates:
                if url in seen:
                    continue
                seen.add(url)
                
            if domain_filter:
                domain = urlparse(url).netloc
                if domain_filter.lower() not in domain.lower():
                    continue
                    
            final_urls.append(url)
            
            if limit and len(final_urls) >= limit:
                break
                
        if not final_urls:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="No URLs matched the filtering criteria.")
            
        try:
            first = True
            for url in final_urls:
                if first:
                    webbrowser.open_new(url)
                    first = False
                else:
                    webbrowser.open_new_tab(url)
                    
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"message": f"Successfully restored browser session with {len(final_urls)} tabs."}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"Failed to restore browser session: {str(e)}"
            )

def get_browser_session_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        id="RestoreBrowserSession",
        version="1.0.0",
        permissions=["browser"],
        execution_mode="sync",
        factory=RestoreBrowserSessionCapability
    )
