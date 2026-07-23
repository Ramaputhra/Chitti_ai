import os
from typing import Any, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.platform.shared.models.ai import ToolInvocation

class CreateDirectoryCapability(ICapability):
    """Capability to create a directory."""
    
    @property
    def name(self) -> str:
        return "CreateDirectory"
        
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
            description="Creates a directory if it doesn't already exist.",
            version="1.0",
            tools=[]
        )
        
    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        path = invocation.arguments.get("path")
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    summary=f"Created directory: {path}",
                    data={"created": True, "path": path}
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    summary=f"Directory already exists: {path}",
                    data={"created": False, "path": path}
                )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                summary=f"Failed to create directory {path}: {str(e)}"
            )
