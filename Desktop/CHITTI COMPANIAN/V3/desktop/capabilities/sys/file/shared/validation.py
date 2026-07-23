"""
Filesystem Shared Primitive

This module is part of the frozen filesystem infrastructure.
Only functionality proven by at least two capabilities may be added.
Capability-specific logic is prohibited.
"""
import os
from typing import Optional
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode

def validate_source_exists(source: str) -> Optional[ExecutionResult]:
    """Validates that a source path exists."""
    if not os.path.exists(source):
        return ExecutionResult(status=ExecutionStatus.FAILED, error_code=ExecutionErrorCode.SOURCE_NOT_FOUND)
    return None

def validate_destination_overwrite(destination: str, overwrite: bool) -> Optional[ExecutionResult]:
    """Validates overwrite rules for a destination."""
    if os.path.exists(destination):
        if not overwrite:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_code=ExecutionErrorCode.FILE_ALREADY_EXISTS)
    return None

def validate_source_and_destination(source: str, destination: str, overwrite: bool) -> Optional[ExecutionResult]:
    """Combined validation for capabilities like copy and move."""
    err = validate_source_exists(source)
    if err:
        return err
    return validate_destination_overwrite(destination, overwrite)
