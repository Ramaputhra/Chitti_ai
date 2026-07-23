import os
import subprocess
import logging
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.paths import normalize_path
from desktop.capabilities.sys.file.shared.validation import validate_source_exists
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

logger = logging.getLogger(__name__)

class SysFileOpenAdapter:
    """
    Physical implementation for the 'sys.file.open' capability on Windows.
    Now supports opening Workspace Profiles via WorkspaceRuntime.
    """
    
    def __init__(self, workspace_runtime=None):
        self.workspace_runtime = workspace_runtime

    def execute(self, path: str) -> ExecutionResult:
        logger.info(f"sys.file.open executing for: {path}")
        
        # Check if it's a workspace request
        if path.startswith("workspace:"):
            if not self.workspace_runtime:
                return ExecutionResult(status=ExecutionStatus.FAILED, error_message="WorkspaceRuntime not available.")
            workspace_id = path.split(":", 1)[1]
            workspace = self.workspace_runtime.get_workspace(workspace_id)
            if not workspace:
                return ExecutionResult(status=ExecutionStatus.FAILED, error_message=f"Workspace {workspace_id} not found.")
            
            # Logic to open the workspace (launch apps, open folders, etc)
            for f in workspace.folders:
                os.startfile(f)
            for app in workspace.applications:
                # Stub for app launching
                logger.info(f"Would launch app: {app}")
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
        
        path = normalize_path(path)
        
        validation_error = validate_source_exists(path)
        if validation_error:
            logger.error(f"Path does not exist: {path}")
            return validation_error
            
        try:
            os.startfile(path)
            logger.info(f"Successfully requested OS to open {path}")
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
        except Exception as e:
            logger.error(f"Failed to open path: {e}")
            return map_fs_error(e)




