import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.paths import normalize_path
from desktop.capabilities.sys.file.shared.validation import validate_source_exists
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

class SysFileSearchAdapter:
    """
    Physical implementation for the 'sys.file.search' capability.
    Acts as a query engine with declarative filtering.
    """
    
    def execute(
        self, 
        location: str, 
        query: str = "*", 
        recursive: bool = True,
        include_directories: bool = False,
        file_types: Optional[List[str]] = None,
        modified_after: str = "",
        modified_before: str = "",
        min_size: int = -1,
        max_size: int = -1,
        limit: int = 50,
        sort_by: str = "modified_desc"
    ) -> ExecutionResult:
        
        if not location:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, 
                error_code=ExecutionErrorCode.MISSING_REQUIRED_PARAMETER,
                error_message="'location' parameter is required for search."
            )
            
        try:
            location = normalize_path(location)
            validation_error = validate_source_exists(location)
            if validation_error:
                return validation_error
                
            base_path = Path(location)
            
            # 1. Location & Name Match (Wildcard)
            # Use rglob for recursive, glob for non-recursive
            iterator = base_path.rglob(query) if recursive else base_path.glob(query)
            
            results = []
            
            # Convert dates to timestamps if provided
            after_ts = datetime.fromisoformat(modified_after).timestamp() if modified_after else None
            before_ts = datetime.fromisoformat(modified_before).timestamp() if modified_before else None
            
            # Normalize file_types for safe comparison
            if file_types:
                file_types = [ext.lower() if ext.startswith('.') else f".{ext.lower()}" for ext in file_types]
                
            for p in iterator:
                # 2. Directory filter
                is_dir = p.is_dir()
                if is_dir and not include_directories:
                    continue
                    
                # 3. Extension filter (only applies to files)
                if not is_dir and file_types:
                    if p.suffix.lower() not in file_types:
                        continue
                        
                # 4. Size & Date filter (requires stat)
                try:
                    stat = p.stat()
                except OSError:
                    continue # Skip files we can't access
                    
                # Size filter (skip directories for size logic)
                if not is_dir:
                    if min_size >= 0 and stat.st_size < min_size:
                        continue
                    if max_size >= 0 and stat.st_size > max_size:
                        continue
                
                # Date filter
                if after_ts and stat.st_mtime < after_ts:
                    continue
                if before_ts and stat.st_mtime > before_ts:
                    continue
                    
                # If it passes all filters, construct the rich output
                results.append({
                    "path": str(p),
                    "name": p.name,
                    "extension": p.suffix if not is_dir else "",
                    "is_directory": is_dir,
                    "size": stat.st_size if not is_dir else 0,
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime,
                    "attributes": {
                        # Simplified attributes for cross-platform compatibility
                        "hidden": p.name.startswith('.'),
                        "readonly": not os.access(str(p), os.W_OK)
                    }
                })
                
            # 5. Sort
            def sort_key(x):
                if sort_by == "modified_desc": return -x["modified_time"]
                elif sort_by == "modified_asc": return x["modified_time"]
                elif sort_by == "size_desc": return -x["size"]
                elif sort_by == "size_asc": return x["size"]
                elif sort_by == "name_asc": return x["name"].lower()
                elif sort_by == "name_desc": return x["name"].lower() # We'll reverse later
                return -x["modified_time"] # Default
                
            results.sort(key=sort_key, reverse=(sort_by == "name_desc"))
            
            # 6. Limit
            if limit > 0:
                results = results[:limit]
                
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={
                    "resource_type": "filesystem",
                    "results": results,
                    "count": len(results)
                }
            )
            
        except ValueError as e:
            # Catch datetime parse errors
            return ExecutionResult(status=ExecutionStatus.FAILED, error_code=ExecutionErrorCode.UNKNOWN_ERROR, error_message=f"Date parsing error: {e}")
        except Exception as e:
            return map_fs_error(e)
