import pytest
import os
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.delete.adapter import SysFileDeleteAdapter

def test_delete_adapter_missing_params():
    adapter = SysFileDeleteAdapter()
    res = adapter.execute(targets=[])
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.MISSING_REQUIRED_PARAMETER

def test_delete_adapter_missing_source(temp_fs):
    adapter = SysFileDeleteAdapter()
    res = adapter.execute(targets=[str(temp_fs / "does_not_exist.txt")])
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.SOURCE_NOT_FOUND

def test_delete_adapter_success(temp_fs):
    adapter = SysFileDeleteAdapter()
    
    src1 = temp_fs / "file1.txt"
    src1.write_text("hello")
    dir1 = temp_fs / "dir1"
    dir1.mkdir()
    (dir1 / "file2.txt").write_text("world")
    
    res = adapter.execute(targets=[str(src1), str(dir1)])
    assert res.status == ExecutionStatus.SUCCESS
    
    assert not src1.exists()
    assert not dir1.exists()
