"""
Filesystem Shared Primitive

This module is part of the frozen filesystem infrastructure.
Only functionality proven by at least two capabilities may be added.
Capability-specific logic is prohibited.
"""
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode

def map_fs_error(e: Exception) -> ExecutionResult:
    """Maps common filesystem exceptions to strongly typed ExecutionResults."""
    if isinstance(e, PermissionError):
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            error_code=ExecutionErrorCode.ACCESS_DENIED,
            error_message=str(e)
        )
    elif isinstance(e, FileNotFoundError):
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            error_code=ExecutionErrorCode.PATH_NOT_FOUND,
            error_message=str(e)
        )
    else:
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            error_code=ExecutionErrorCode.UNKNOWN_ERROR,
            error_message=str(e)
        )
