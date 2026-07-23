import os
from typing import Any, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.platform.shared.models.ai import ToolInvocation

class ListDirectoryCapability(ICapability):
    """Capability to list contents of a directory."""
    
    @property
    def name(self) -> str:
        return "ListDirectory"
        
    @property
    def state(self) -> Any:
        return None
        
    def initialize(self) -> None:
        pass
        
    def shutdown(self) -> None:
        pass
        
    def discover_tools(self) -> List[ToolDescriptor]:
        return []
        
    def validate(self, invocation: ToolInvocation) -> bool:
        return "path" in invocation.arguments
        
    def cancel(self, invocation_id: str) -> None:
        pass
        
    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Returns a list of files in a directory.",
            version="1.0",
            tools=[]
        )
        
    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        path = invocation.arguments.get("path")
        if not os.path.exists(path):
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                summary=f"Path not found: {path}"
            )
            
        try:
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                summary=f"Found {len(files)} files",
                data={"files": files, "path": path}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                summary=f"Error listing directory: {str(e)}"
            )
