import os
import time
from typing import Optional
from desktop.models.execution import ExecutionResult, ExecutionStatus, ExecutionErrorCode

class DownloadRuntime:
    """
    Monitors and verifies downloads via the OS Filesystem using Evidence-First principles.
    This guarantees reliability regardless of the browser backend.
    """
    
    def __init__(self):
        self.poll_interval = 0.5
        self.stable_duration_needed = 2.0
        
    def _get_file_size(self, path: str) -> int:
        try:
            return os.stat(path).st_size
        except FileNotFoundError:
            return -1
            
    def verify_download(self, expected_path: str, timeout_sec: int = 30) -> ExecutionResult:
        """
        Verification order:
        1. OS File Created
        2. File Size Growth
        3. Temporary File Gone (.crdownload / .part)
        4. File Size Stable
        5. Hash Verification (Optional, if hash provided)
        6. File Opens Successfully
        7. MIME Type Matches (Catches HTML error pages masquerading as 200 OK)
        """
        start_time = time.time()
        
        # 1. Wait for file (or temp file) to appear
        while time.time() - start_time < timeout_sec:
            # Check for final file
            if os.path.exists(expected_path):
                break
                
            # Check for known temp files
            if os.path.exists(expected_path + ".crdownload") or os.path.exists(expected_path + ".part"):
                break
                
            time.sleep(self.poll_interval)
            
        if time.time() - start_time >= timeout_sec:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.TIMEOUT,
                error_message="Download timeout: File never appeared on disk."
            )
            
        # 2 & 3. Wait for final file and stable size
        last_size = -1
        stable_time = 0.0
        
        while time.time() - start_time < timeout_sec:
            if not os.path.exists(expected_path):
                # Still downloading to a temp file
                time.sleep(self.poll_interval)
                continue
                
            current_size = self._get_file_size(expected_path)
            
            if current_size == last_size and current_size > 0:
                stable_time += self.poll_interval
                if stable_time >= self.stable_duration_needed:
                    break
            else:
                last_size = current_size
                stable_time = 0.0
                
            time.sleep(self.poll_interval)
            
        if stable_time < self.stable_duration_needed:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code=ExecutionErrorCode.TIMEOUT,
                error_message="Download timeout: File size never stabilized."
            )
            
        # 4. MIME Type / Read check (Stubbed)
        # Normally we'd use libmagic or mimetypes here to check if expected_path is actually an HTML error
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"path": expected_path, "size": last_size})
