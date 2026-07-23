import pytest
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.create.adapter import SysFileCreateAdapter

def test_sys_file_create_adapter_file(temp_fs):
    adapter = SysFileCreateAdapter()
    
    dst = temp_fs / "new_folder" / "test.txt"
    
    res = adapter.execute(str(dst), is_directory=False, content="hello", collision_policy="fail")
    assert res.status == ExecutionStatus.SUCCESS
    assert dst.exists()
    assert dst.is_file()
    assert dst.read_text(encoding='utf-8') == "hello"

def test_sys_file_create_adapter_directory(temp_fs):
    adapter = SysFileCreateAdapter()
    
    dst = temp_fs / "nested" / "folder"
    
    res = adapter.execute(str(dst), is_directory=True, collision_policy="fail")
    assert res.status == ExecutionStatus.SUCCESS
    assert dst.exists()
    assert dst.is_dir()

def test_sys_file_create_adapter_collision_fail(temp_fs):
    adapter = SysFileCreateAdapter()
    
    dst = temp_fs / "test.txt"
    dst.write_text("old")
    
    res = adapter.execute(str(dst), is_directory=False, content="new", collision_policy="fail")
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.FILE_ALREADY_EXISTS
    assert dst.read_text(encoding='utf-8') == "old"

def test_sys_file_create_adapter_collision_overwrite(temp_fs):
    adapter = SysFileCreateAdapter()
    
    dst = temp_fs / "test.txt"
    dst.write_text("old")
    
    res = adapter.execute(str(dst), is_directory=False, content="new", collision_policy="overwrite")
    assert res.status == ExecutionStatus.SUCCESS
    assert dst.read_text(encoding='utf-8') == "new"

def test_sys_file_create_adapter_collision_skip(temp_fs):
    adapter = SysFileCreateAdapter()
    
    dst = temp_fs / "test.txt"
    dst.write_text("old")
    
    res = adapter.execute(str(dst), is_directory=False, content="new", collision_policy="skip")
    assert res.status == ExecutionStatus.SUCCESS
    assert dst.read_text(encoding='utf-8') == "old"
