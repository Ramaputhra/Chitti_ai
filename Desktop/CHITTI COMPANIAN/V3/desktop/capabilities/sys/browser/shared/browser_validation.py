import re
from typing import Optional
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode

def validate_url(url: str) -> Optional[ExecutionResult]:
    """Validates if a string is a properly formatted URL."""
    if not url:
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            error_code=ExecutionErrorCode.MISSING_REQUIRED_PARAMETER,
            error_message="URL is required."
        )
        
    # Basic URL validation
    pattern = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
    if not re.match(pattern, url):
        # Auto-prefix http if missing
        if not url.startswith('http'):
            return None # The adapter can prefix it
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            error_code=ExecutionErrorCode.UNKNOWN_ERROR,
            error_message=f"Invalid URL format: {url}"
        )
        
    return None
