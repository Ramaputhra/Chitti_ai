import os
import pathlib
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.paths import normalize_path
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

class SysFileCreateAdapter:
    """
    Physical implementation for the 'sys.file.create' capability.
    Pure execution primitive relying on frozen shared infrastructure.
    """
    
    def execute(self, path: str, is_directory: bool = False, content: str = "", collision_policy: str = "fail") -> ExecutionResult:
        try:
            path = normalize_path(path)
            
            if os.path.exists(path):
                if collision_policy == "fail":
                    return ExecutionResult(status=ExecutionStatus.FAILED, error_code=ExecutionErrorCode.FILE_ALREADY_EXISTS)
                elif collision_policy == "skip":
                    return ExecutionResult(status=ExecutionStatus.SUCCESS)
                elif collision_policy == "overwrite":
                    pass
                else:
                    return ExecutionResult(status=ExecutionStatus.FAILED, error_code=ExecutionErrorCode.UNKNOWN_ERROR, error_message=f"Invalid collision policy: {collision_policy}")

            # Ensure parent directories exist
            parent_dir = os.path.dirname(path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                
            if is_directory:
                return self._create_directory(path)
            else:
                return self._create_file(path, content)
                
        except Exception as e:
            return map_fs_error(e)
            
    def _create_directory(self, path: str) -> ExecutionResult:
        # exist_ok=True to handle race conditions safely
        os.makedirs(path, exist_ok=True)
        return ExecutionResult(status=ExecutionStatus.SUCCESS)
        
    def _create_file(self, path: str, content: str) -> ExecutionResult:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return ExecutionResult(status=ExecutionStatus.SUCCESS)
