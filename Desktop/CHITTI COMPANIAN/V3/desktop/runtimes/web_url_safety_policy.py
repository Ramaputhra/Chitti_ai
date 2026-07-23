from enum import Enum

class SafetyAction(Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"

class UrlSafetyPolicyRuntime:
    """
    Evaluates URLs against Rule 22: Safe Browsing Policy.
    Blocks known adult, malware, phishing, and piracy domains.
    """
    
    def __init__(self):
        # Stub blocklist for architectural purposes
        self.blocklist = [
            "malware.example.com",
            "phishing.example.com",
            "adult.example.com"
        ]
        
    def evaluate(self, url: str) -> SafetyAction:
        if not url:
            return SafetyAction.BLOCK
            
        url_lower = url.lower()
        
        for bad_domain in self.blocklist:
            if bad_domain in url_lower:
                return SafetyAction.BLOCK
                
        # Normally would include regex patterns or an API call to a safe browsing service
        return SafetyAction.ALLOW
