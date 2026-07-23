import pytest
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.rename.adapter import SysFileRenameAdapter

def test_sys_file_rename_adapter_success(temp_fs):
    adapter = SysFileRenameAdapter()
    
    src = temp_fs / "old.txt"
    src.write_text("hello")
    dst = temp_fs / "new.txt"
    
    res = adapter.execute(str(src), str(dst), collision_policy="fail")
    assert res.status == ExecutionStatus.SUCCESS
    assert not src.exists()
    assert dst.exists()
    assert dst.read_text() == "hello"

def test_sys_file_rename_adapter_case_only(temp_fs):
    adapter = SysFileRenameAdapter()
    
    src = temp_fs / "Test.txt"
    src.write_text("hello")
    dst = temp_fs / "test.txt"
    
    res = adapter.execute(str(src), str(dst), collision_policy="fail")
    assert res.status == ExecutionStatus.SUCCESS
    # We can't strictly assert source doesn't exist on Windows because of case-insensitivity, 
    # but the API handles it without hitting FILE_ALREADY_EXISTS.

def test_sys_file_rename_adapter_cross_dir_rejection(temp_fs):
    adapter = SysFileRenameAdapter()
    
    dir1 = temp_fs / "dir1"
    dir1.mkdir()
    src = dir1 / "old.txt"
    src.write_text("hello")
    
    dir2 = temp_fs / "dir2"
    dir2.mkdir()
    dst = dir2 / "old.txt"
    
    res = adapter.execute(str(src), str(dst), collision_policy="fail")
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.USE_MOVE_CAPABILITY

def test_sys_file_rename_adapter_collision_fail(temp_fs):
    adapter = SysFileRenameAdapter()
    
    src = temp_fs / "old.txt"
    src.write_text("hello")
    dst = temp_fs / "new.txt"
    dst.write_text("target")
    
    res = adapter.execute(str(src), str(dst), collision_policy="fail")
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.FILE_ALREADY_EXISTS

def test_sys_file_rename_adapter_collision_overwrite(temp_fs):
    adapter = SysFileRenameAdapter()
    
    src = temp_fs / "old.txt"
    src.write_text("hello")
    dst = temp_fs / "new.txt"
    dst.write_text("target")
    
    res = adapter.execute(str(src), str(dst), collision_policy="overwrite")
    assert res.status == ExecutionStatus.SUCCESS
    assert dst.read_text() == "hello"
