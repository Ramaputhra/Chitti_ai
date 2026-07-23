import os
import shutil
from pathlib import Path
from typing import List

from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.paths import normalize_path
from desktop.capabilities.sys.file.shared.validation import validate_source_exists
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

class SysFileDeleteAdapter:
    """
    Physical implementation for the 'sys.file.delete' capability.
    Performs permanent, irreversible deletion. Guarded by physical confirmation in the UI.
    """
    
    def execute(self, targets: List[str]) -> ExecutionResult:
        if not targets:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, 
                error_code=ExecutionErrorCode.MISSING_REQUIRED_PARAMETER,
                error_message="targets parameter is required."
            )
            
        try:
            normalized_targets = []
            for target in targets:
                norm_target = normalize_path(target)
                if validation_error := validate_source_exists(norm_target):
                    return validation_error # Returns SOURCE_NOT_FOUND if missing
                normalized_targets.append(Path(norm_target))
                
            for target in normalized_targets:
                if target.is_file() or target.is_symlink():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
                    
            # Verify paths are completely missing
            for target in normalized_targets:
                if target.exists():
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                        error_message=f"Permanent deletion failed. {target} still exists."
                    )
            
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
            
        except Exception as e:
            return map_fs_error(e)
