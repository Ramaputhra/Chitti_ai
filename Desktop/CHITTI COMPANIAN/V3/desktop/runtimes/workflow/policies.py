import asyncio
import logging
from typing import Callable, Awaitable, Any
from desktop.platform.shared.models.workflow import RetryPolicy
from desktop.runtimes.workflow.models import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)

class RetryManager:
    """
    Executes a callable with respect to a RetryPolicy.
    """
    @staticmethod
    async def execute_with_retry(
        policy: RetryPolicy,
        func: Callable[[], Awaitable[ExecutionResult]]
    ) -> ExecutionResult:
        attempt = 1
        max_attempts = policy.max_attempts if policy else 1
        backoff = policy.backoff_ms if policy else 1000
        
        while attempt <= max_attempts:
            try:
                result = await func()
                
                # If success or cancelled, return immediately
                if result.status in (ExecutionStatus.SUCCESS, ExecutionStatus.CANCELLED):
                    return result
                    
                # If failed, check if we should retry
                if attempt >= max_attempts:
                    return result
                    
                logger.warning(f"[RetryManager] Attempt {attempt} failed: {result.error_message}. Retrying in {backoff}ms...")
                
            except Exception as e:
                logger.exception(f"[RetryManager] Unhandled exception on attempt {attempt}: {e}")
                if attempt >= max_attempts:
                    return ExecutionResult(status=ExecutionStatus.FAILURE, error_message=str(e))
            
            # Wait before next attempt
            await asyncio.sleep(backoff / 1000.0)
            attempt += 1
            
        return ExecutionResult(status=ExecutionStatus.FAILURE, error_message="Max retries exceeded.")
