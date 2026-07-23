import pytest
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.move.adapter import SysFileMoveAdapter

def test_sys_file_move_adapter_success(temp_fs):
    adapter = SysFileMoveAdapter()
    
    src = temp_fs / "src.txt"
    src.write_text("hello")
    dst = temp_fs / "dst.txt"
    
    res = adapter.execute(str(src), str(dst), overwrite=False)
    assert res.status == ExecutionStatus.SUCCESS
    assert not src.exists()
    assert dst.exists()
    assert dst.read_text() == "hello"

def test_sys_file_move_adapter_already_exists(temp_fs):
    adapter = SysFileMoveAdapter()
    
    src = temp_fs / "src.txt"
    src.write_text("hello")
    dst = temp_fs / "dst.txt"
    dst.write_text("old")
    
    res = adapter.execute(str(src), str(dst), overwrite=False)
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.FILE_ALREADY_EXISTS
    assert src.exists()
    assert dst.read_text() == "old"



