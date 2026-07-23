import os
from typing import Any, List, Dict

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.platform.shared.models.ai import ToolInvocation

class CategorizeFilesCapability(ICapability):
    """Capability to categorize files based on extension mapping."""
    
    @property
    def name(self) -> str:
        return "CategorizeFiles"
        
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
        return "files" in invocation.arguments and "mapping" in invocation.arguments
        
    def cancel(self, invocation_id: str) -> None:
        pass
        
    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Categorizes a list of files according to a provided extension mapping.",
            version="1.0",
            tools=[]
        )
        
    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        files: List[str] = invocation.arguments.get("files", [])
        mapping: Dict[str, str] = invocation.arguments.get("mapping", {})
        
        # Default category if extension isn't mapped
        default_category = "Others"
        
        categorized_files = {}
        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            category = mapping.get(ext, default_category)
            
            if category not in categorized_files:
                categorized_files[category] = []
            categorized_files[category].append(file)
            
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            summary=f"Categorized {len(files)} files into {len(categorized_files)} categories.",
            data={"categorized_files": categorized_files}
        )
