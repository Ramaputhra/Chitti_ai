import os
import shutil
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.validation import validate_source_and_destination
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

class SysFileCopyAdapter:
    """
    Physical implementation for the 'sys.file.copy' capability.
    Pure execution primitive.
    """
    
    def execute(self, source: str, destination: str, overwrite: bool = False) -> ExecutionResult:
        validation_error = validate_source_and_destination(source, destination, overwrite)
        if validation_error:
            return validation_error
                
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=overwrite)
            else:
                shutil.copy2(source, destination)
                
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
            
        except Exception as e:
            return map_fs_error(e)



