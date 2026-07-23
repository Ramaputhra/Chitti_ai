import os
import zipfile
import tarfile
from pathlib import Path
from typing import List, Dict, Any

from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.paths import normalize_path
from desktop.capabilities.sys.file.shared.validation import validate_source_exists
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

FORMAT_EXTENSIONS = {
    "zip": ".zip",
    "tar": ".tar",
    "gztar": ".tar.gz",
    "bztar": ".tar.bz2",
    "xztar": ".tar.xz"
}

class SysFileCompressAdapter:
    """
    Physical implementation for the 'sys.file.compress' capability.
    Batch operation design.
    """
    
    def execute(
        self, 
        sources: List[str], 
        destination_dir: str, 
        archive_name: str,
        format: str = "zip",
        compression_level: int = -1,
        collision_policy: str = "fail"
    ) -> ExecutionResult:
        
        if not sources or not destination_dir or not archive_name:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, 
                error_code=ExecutionErrorCode.MISSING_REQUIRED_PARAMETER,
                error_message="sources, destination_dir, and archive_name are required."
            )
            
        if format not in FORMAT_EXTENSIONS:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.INVALID_PATH, # Reusing for invalid format
                error_message=f"Unsupported format: {format}"
            )
            
        try:
            # 1. Normalize and validate sources
            normalized_sources = []
            for src in sources:
                norm_src = normalize_path(src)
                if validation_error := validate_source_exists(norm_src):
                    return validation_error # Returns SOURCE_NOT_FOUND if missing
                normalized_sources.append(Path(norm_src))
                
            # 2. Prepare destination
            dest_dir = Path(normalize_path(destination_dir))
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            ext = FORMAT_EXTENSIONS[format]
            if not archive_name.lower().endswith(ext):
                archive_name += ext
                
            archive_path = dest_dir / archive_name
            
            # 3. Collision handling
            if archive_path.exists():
                if collision_policy == "fail":
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED, 
                        error_code=ExecutionErrorCode.FILE_ALREADY_EXISTS
                    )
                elif collision_policy == "overwrite":
                    pass # We will overwrite
                else:
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED, 
                        error_code=ExecutionErrorCode.UNKNOWN_ERROR, 
                        error_message=f"Invalid collision policy: {collision_policy}"
                    )
                    
            # 4. Create Archive
            expected_count = 0
            
            if format == "zip":
                compress_type = zipfile.ZIP_DEFLATED
                # Note: compression_level was added in Python 3.7+ for zipfile
                kwargs = {"compression": compress_type}
                if compression_level >= 0:
                    kwargs["compresslevel"] = compression_level
                    
                with zipfile.ZipFile(archive_path, 'w', **kwargs) as zf:
                    for src in normalized_sources:
                        if src.is_file():
                            zf.write(src, arcname=src.name)
                            expected_count += 1
                        else:
                            for root, dirs, files in os.walk(src):
                                root_path = Path(root)
                                for file in files:
                                    file_path = root_path / file
                                    # arcname ensures directory structure is preserved relative to the source
                                    arcname = src.name / file_path.relative_to(src)
                                    zf.write(file_path, arcname=str(arcname))
                                    expected_count += 1
            else:
                # tarfile handling
                mode_map = {
                    "tar": "w",
                    "gztar": "w:gz",
                    "bztar": "w:bz2",
                    "xztar": "w:xz"
                }
                mode = mode_map[format]
                with tarfile.open(archive_path, mode) as tf:
                    for src in normalized_sources:
                        if src.is_file():
                            tf.add(src, arcname=src.name)
                            expected_count += 1
                        else:
                            # tarfile.add adds directory recursively by default
                            tf.add(src, arcname=src.name)
                            # We still need expected count, so we have to count files
                            for root, dirs, files in os.walk(src):
                                expected_count += len(files)
                                
            # 5. Internal Verification (archive_exists, archive_size_valid, archive_readable)
            if not archive_path.exists():
                raise Exception("Archive was not created on disk.")
                
            stat = archive_path.stat()
            if stat.st_size == 0 and expected_count > 0:
                raise Exception("Archive size is 0 but sources were provided.")
                
            # Verify readability and entry count
            actual_count = 0
            if format == "zip":
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    if zf.testzip() is not None:
                        raise Exception("Archive is corrupt (testzip failed).")
                    actual_count = len([info for info in zf.infolist() if not info.is_dir()])
            else:
                with tarfile.open(archive_path, 'r') as tf:
                    actual_count = sum(1 for m in tf.getmembers() if m.isfile())
                    
            if actual_count != expected_count:
                raise Exception(f"Archive entry count mismatch. Expected {expected_count}, got {actual_count}")
                
            # 6. Format Output
            result_meta = {
                "path": str(archive_path),
                "name": archive_path.name,
                "extension": ext,
                "is_directory": False,
                "size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "attributes": {
                    "hidden": archive_path.name.startswith('.'),
                    "readonly": not os.access(str(archive_path), os.W_OK)
                }
            }
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={
                    "resource_type": "filesystem",
                    "results": [result_meta],
                    "count": 1
                }
            )
            
        except Exception as e:
            # If an error happens, we should try to clean up a partial archive
            if 'archive_path' in locals() and archive_path.exists():
                try:
                    archive_path.unlink()
                except OSError:
                    pass
            return map_fs_error(e)
