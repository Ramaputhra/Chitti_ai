from typing import Dict, Any, Optional
import os
import glob
from desktop.platform.shared.models.execution import ExecutionResult, ExecutionStatus
from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class FindFileCapability:
    """
    Finds files on the filesystem based on a pattern or name.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(
            category="Filesystem",
            supports_undo=False
        )
        
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "File name or glob pattern (e.g. '*.txt', 'report.pdf')"
                },
                "search_path": {
                    "type": "string",
                    "description": "Directory to search in"
                }
            },
            "required": ["pattern", "search_path"]
        }
        
    async def execute(self, params: Dict[str, Any], context: Any) -> ExecutionResult:
        pattern = params.get("pattern")
        search_path = params.get("search_path")
        
        if not os.path.exists(search_path):
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error=f"Directory does not exist: {search_path}"
            )
            
        search_glob = os.path.join(search_path, "**", pattern)
        matches = glob.glob(search_glob, recursive=True)
        
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            output=f"Found {len(matches)} files.",
            metadata={"files": matches, "verification": {"files_found": len(matches)}}
        )
