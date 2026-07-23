import pytest
import os
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.recycle.adapter import SysFileRecycleAdapter

def test_recycle_adapter_missing_params():
    adapter = SysFileRecycleAdapter()
    res = adapter.execute(targets=[])
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.MISSING_REQUIRED_PARAMETER

def test_recycle_adapter_missing_source(temp_fs):
    adapter = SysFileRecycleAdapter()
    res = adapter.execute(targets=[str(temp_fs / "does_not_exist.txt")])
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.SOURCE_NOT_FOUND

def test_recycle_adapter_success(temp_fs):
    adapter = SysFileRecycleAdapter()
    
    src1 = temp_fs / "file1.txt"
    src1.write_text("hello")
    src2 = temp_fs / "file2.txt"
    src2.write_text("world")
    
    res = adapter.execute(targets=[str(src1), str(src2)])
    assert res.status == ExecutionStatus.SUCCESS
    
    assert not src1.exists()
    assert not src2.exists()
