import os
import shutil
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.validation import validate_source_and_destination
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

class SysFileMoveAdapter:
    """
    Physical implementation for the 'sys.file.move' capability.
    Pure execution primitive.
    """
    
    def execute(self, source: str, destination: str, overwrite: bool = False) -> ExecutionResult:
        validation_error = validate_source_and_destination(source, destination, overwrite)
        if validation_error:
            return validation_error
                
        try:
            shutil.move(source, destination)
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
            
        except Exception as e:
            return map_fs_error(e)



