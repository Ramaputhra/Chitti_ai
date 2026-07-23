import os
import shutil
from typing import Any, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.platform.shared.models.ai import ToolInvocation

class MoveFileCapability(ICapability):
    """Capability to move a file."""
    
    @property
    def name(self) -> str:
        return "MoveFile"
        
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
        return "source" in invocation.arguments and "destination" in invocation.arguments
        
    def cancel(self, invocation_id: str) -> None:
        pass
        
    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Moves a file from a source path to a destination path.",
            version="1.0",
            tools=[]
        )
        
    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        source = invocation.arguments.get("source")
        destination = invocation.arguments.get("destination")
        
        try:
            if not os.path.exists(source):
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    summary=f"Source file not found: {source}"
                )
                
            shutil.move(source, destination)
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                summary=f"Moved file to: {destination}",
                data={"source": source, "destination": destination}
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                summary=f"Failed to move file from {source} to {destination}: {str(e)}"
            )
