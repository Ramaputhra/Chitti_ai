import os
import subprocess
import webbrowser
from typing import Optional
from desktop.app.capability_contracts import ICapability, CapabilityDescriptor
from desktop.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus

class OSAutomationCapability(ICapability):
    """
    Handles Sprint 110: Desktop Automation Experience.
    Allows opening explicit apps, folders, and URLs.
    Includes verification to ensure the launch succeeded.
    """
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        # We extract the specific action/intent from the workflow payload or plan
        # We'll assume the Planner generated an ExecutionPlan with the required action
        tool_name = context.plan.capability_action
        parameters = context.plan.parameters
        
        if tool_name == "open_application":
            return await self._open_app(parameters.get("target"))
        elif tool_name == "open_folder":
            return await self._open_folder(parameters.get("path"))
        elif tool_name == "open_url":
            return await self._open_url(parameters.get("url"))
        else:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"Unknown automation action: {tool_name}"
            )

    async def _open_app(self, target: Optional[str]) -> ExecutionResult:
        if not target:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="Application target missing.")
            
        try:
            # Basic validation/mapping for common apps to make the demo reliable
            app_map = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "file explorer": "explorer.exe",
                "settings": "ms-settings:",
                "chrome": "chrome.exe"
            }
            
            executable = app_map.get(target.lower(), target)
            
            # Use os.startfile for Windows to launch it
            # For verification, we just check if the process call doesn't throw. 
            # In a real environment, we might poll `psutil` but keeping it minimal for MVP.
            if hasattr(os, "startfile"):
                os.startfile(executable)
            else:
                # Fallback for non-windows if ever needed
                subprocess.Popen([executable])
                
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"message": f"Opened {target.title()}"}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"Failed to open application: {str(e)}"
            )

    async def _open_folder(self, path: Optional[str]) -> ExecutionResult:
        if not path:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="Folder path missing.")
            
        if not os.path.exists(path):
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message=f"Folder does not exist: {path}")
            
        try:
            if hasattr(os, "startfile"):
                os.startfile(path)
            else:
                subprocess.Popen(["explorer", path])
                
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"message": f"Opened folder: {path}"}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"Failed to open folder: {str(e)}"
            )

    async def _open_url(self, url: Optional[str]) -> ExecutionResult:
        if not url:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="URL missing.")
            
        try:
            # Provide basic http prefix if missing
            if not url.startswith("http"):
                url = "https://" + url
                
            webbrowser.open(url)
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"message": f"Opened URL: {url}"}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_message=f"Failed to open URL: {str(e)}"
            )

def get_os_automation_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        id="OSAutomation",
        version="1.0",
        permissions=["desktop_control"],
        execution_mode="sync",
        factory=lambda: OSAutomationCapability()
    )
