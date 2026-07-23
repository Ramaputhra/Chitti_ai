import os
import ctypes
from ctypes import wintypes
from typing import List

from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.shared.paths import normalize_path
from desktop.capabilities.sys.file.shared.validation import validate_source_exists
from desktop.capabilities.sys.file.shared.error_mapping import map_fs_error

class SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("wFunc", wintypes.UINT),
        ("pFrom", wintypes.LPCWSTR),
        ("pTo", wintypes.LPCWSTR),
        ("fFlags", wintypes.WORD),
        ("fAnyOperationsAborted", wintypes.BOOL),
        ("hNameMappings", wintypes.LPVOID),
        ("lpszProgressTitle", wintypes.LPCWSTR)
    ]

FO_DELETE = 0x0003
FOF_ALLOWUNDO = 0x0040
FOF_NOCONFIRMATION = 0x0010
FOF_NOERRORUI = 0x0400
FOF_SILENT = 0x0004

class SysFileRecycleAdapter:
    """
    Physical implementation for the 'sys.file.recycle' capability.
    Uses native Windows Shell APIs to ensure items are moved to the Recycle Bin.
    """
    
    def execute(self, targets: List[str]) -> ExecutionResult:
        if not targets:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, 
                error_code=ExecutionErrorCode.MISSING_REQUIRED_PARAMETER,
                error_message="targets parameter is required."
            )
            
        try:
            normalized_targets = []
            for target in targets:
                norm_target = normalize_path(target)
                if validation_error := validate_source_exists(norm_target):
                    return validation_error # Returns SOURCE_NOT_FOUND if missing
                normalized_targets.append(norm_target)
                
            # pFrom expects a double-null-terminated string of paths separated by single nulls
            buffer_str = "\0".join(normalized_targets) + "\0\0"
            
            fileop = SHFILEOPSTRUCTW()
            fileop.hwnd = None
            fileop.wFunc = FO_DELETE
            fileop.pFrom = ctypes.cast(ctypes.create_unicode_buffer(buffer_str), wintypes.LPCWSTR)
            fileop.pTo = None
            # FOF_ALLOWUNDO is what sends it to the recycle bin
            fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_NOERRORUI | FOF_SILENT
            fileop.fAnyOperationsAborted = False
            fileop.hNameMappings = None
            fileop.lpszProgressTitle = None
            
            # Execute Shell Operation
            result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
            
            # 0 indicates success in SHFileOperationW
            if result != 0:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                    error_message=f"SHFileOperationW failed with code {result}"
                )
                
            # Verify original paths are missing
            for target in normalized_targets:
                if os.path.exists(target):
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        error_code=ExecutionErrorCode.UNKNOWN_ERROR,
                        error_message=f"Shell API reported success, but {target} still exists."
                    )
            
            return ExecutionResult(status=ExecutionStatus.SUCCESS)
            
        except Exception as e:
            return map_fs_error(e)
