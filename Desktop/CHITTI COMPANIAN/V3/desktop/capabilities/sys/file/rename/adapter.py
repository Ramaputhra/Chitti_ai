import os
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.paths import normalize_path
from desktop.capabilities.sys.file.shared.validation import validate_source_exists
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

class SysFileRenameAdapter:
    """
    Physical implementation for the 'sys.file.rename' capability.
    Pure execution primitive relying on frozen shared infrastructure.
    """
    
    def execute(self, source: str, destination: str, collision_policy: str = "fail") -> ExecutionResult:
        try:
            source = normalize_path(source)
            destination = normalize_path(destination)
            
            validation_error = validate_source_exists(source)
            if validation_error:
                return validation_error
                
            # Cross-directory validation
            source_dir = os.path.dirname(source)
            dest_dir = os.path.dirname(destination)
            
            if source_dir.lower() != dest_dir.lower():
                return ExecutionResult(
                    status=ExecutionStatus.FAILED, 
                    error_code=ExecutionErrorCode.USE_MOVE_CAPABILITY,
                    error_message="Rename must occur in the same directory. Use sys.file.move instead."
                )
            
            # Case-only rename detection (Windows case-insensitivity)
            is_case_only_rename = (source.lower() == destination.lower())
            
            # Collision handling
            if os.path.exists(destination) and not is_case_only_rename:
                if collision_policy == "fail":
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED, 
                        error_code=ExecutionErrorCode.FILE_ALREADY_EXISTS
                    )
                elif collision_policy == "overwrite":
                    pass
                else:
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED, 
                        error_code=ExecutionErrorCode.UNKNOWN_ERROR, 
                        error_message=f"Invalid collision policy: {collision_policy}"
                    )

            # Use os.replace for safe atomic overwrite semantics (unlike os.rename which fails on Windows if dest exists)
            os.replace(source, destination)
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
            
        except Exception as e:
            return map_fs_error(e)
