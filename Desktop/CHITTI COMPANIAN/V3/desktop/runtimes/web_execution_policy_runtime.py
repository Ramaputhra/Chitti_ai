from desktop.models.web_models import WebExecutionMode
from desktop.runtimes.web_url_safety_policy import UrlSafetyPolicyRuntime, SafetyAction

class WebExecutionPolicyException(Exception):
    pass

class WebExecutionPolicyRuntime:
    """
    Determines the WebExecutionMode based on the requested goal/intent.
    Adheres to Constitution Rule 19: Least Intrusive Web Execution
    and Rule 22: Safe Browsing Policy.
    """
    
    def __init__(self):
        self.safety_policy = UrlSafetyPolicyRuntime()
    
    def evaluate_policy(
        self, 
        intent: str, 
        target_url: str = None, 
        requires_auth: bool = False, 
        forces_interactive: bool = False
    ) -> WebExecutionMode:
        
        # Rule 22: Safe Browsing Policy check first
        if target_url:
            safety = self.safety_policy.evaluate(target_url)
            if safety == SafetyAction.BLOCK:
                raise WebExecutionPolicyException(
                    "Target URL violates Rule 22: Safe Browsing Policy."
                )
        
        # Rule 21 & 20: If authentication or explicit interactive interaction is required
        if requires_auth or forces_interactive:
            return WebExecutionMode.INTERACTIVE
            
        # Example naive heuristic
        intent_lower = intent.lower()
        if "search" in intent_lower or "find" in intent_lower:
            return WebExecutionMode.SEARCH
            
        if "download" in intent_lower and "robots.txt" in intent_lower:
            # Simple static files don't need a crawler or browser
            return WebExecutionMode.HTTP_FETCH
            
        if "extract" in intent_lower or "download all" in intent_lower:
            return WebExecutionMode.CRAWL
            
        return WebExecutionMode.HEADLESS
