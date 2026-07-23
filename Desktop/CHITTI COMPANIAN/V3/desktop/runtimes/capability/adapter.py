import traceback
import logging
from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus, ExecutionErrorCode

logger = logging.getLogger(__name__)

class CapabilityAdapter:
    """
    Normalizes all raw Python exceptions into structured ExecutionResults.
    """
    @staticmethod
    async def execute_safe(capability, context) -> ExecutionResult:
        try:
            import inspect
            if inspect.iscoroutinefunction(capability.execute):
                result = await capability.execute(context)
            else:
                result = capability.execute(context)
                
            if not isinstance(result, ExecutionResult):
                logger.error(f"Capability {capability.__class__.__name__} did not return an ExecutionResult.")
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_message="Invalid return type from capability",
                    error_code=ExecutionErrorCode.UNKNOWN_ERROR
                )
            return result
        except Exception as e:
            logger.exception(f"Unhandled exception in capability {capability.__class__.__name__}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=str(e),
                error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                telemetry={"traceback": traceback.format_exc()}
            )
