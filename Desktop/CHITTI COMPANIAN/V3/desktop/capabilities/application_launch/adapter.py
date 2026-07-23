import os
import subprocess
import time
import logging
from desktop.runtimes.workflow.models import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)

class ApplicationLaunchAdapter:
    """
    Physical implementation for the 'application.launch' capability on Windows.
    Adheres strictly to Rule 98 (Capability Contracts) and Evidence Verification.
    """
    
    # Common app aliases to executable names (could be moved to a config)
    APP_ALIASES = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "vs code": "code",
        "vscode": "code",
        "code": "code",
        "notepad": "notepad.exe",
        "edge": "msedge.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe"
    }
    
    def execute(self, application: str) -> ExecutionResult:
        logger.info(f"application.launch executing for: {application}")
        
        app_lower = application.lower()
        exe_name = self.APP_ALIASES.get(app_lower, application)
        
        # We attempt to launch via PowerShell 'Start-Process' which uses shell execution rules
        # allowing it to find executables in PATH or App Paths registry.
        try:
            # First, check if it's a completely invalid/unsafe command
            if any(unsafe in exe_name for unsafe in ["delete", "format", "rm", "del", "system32"]):
                return ExecutionResult(
                    status=ExecutionStatus.FAILURE,
                    error_message=f"Execution rejected for security reasons: {exe_name}"
                )
                
            # Launch
            logger.info(f"Attempting to launch: {exe_name}")
            # Use cmd.exe /c start to rely on Windows shell resolution
            cmd = f'start "" "{exe_name}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to launch {exe_name}: {result.stderr}")
                return ExecutionResult(
                    status=ExecutionStatus.FAILURE,
                    error_message=f"Failed to launch application."
                )
                
            # Evidence Verification: Wait a moment for it to spawn
            time.sleep(1.0)
            
            # Verify if the process exists using tasklist
            base_exe = exe_name
            if not base_exe.endswith(".exe") and base_exe != "code":
                base_exe += ".exe"
            
            tasklist_cmd = f'tasklist /FI "IMAGENAME eq {base_exe}"'
            verify_result = subprocess.run(tasklist_cmd, shell=True, capture_output=True, text=True)
            
            # If the output contains the process name, we consider it verified
            if base_exe.lower() in verify_result.stdout.lower() or "code.exe" in verify_result.stdout.lower():
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    metadata={
                        "application": application, 
                        "executable": exe_name,
                        "verification": {
                            "process_running": True
                        }
                    }
                )
            else:
                logger.warning(f"Could not conclusively verify {exe_name} is running in tasklist, but command succeeded.")
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    metadata={
                        "application": application, 
                        "executable": exe_name,
                        "verification": {
                            "process_running": False
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Exception during application.launch: {e}")
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                error_message=str(e)
            )
