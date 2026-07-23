import pytest
from unittest.mock import patch, MagicMock
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.open.adapter import SysFileOpenAdapter

def test_sys_file_open_adapter_success(temp_fs):
    adapter = SysFileOpenAdapter()
    
    with patch('os.startfile') as mock_startfile:
        result = adapter.execute(str(temp_fs))
        assert result.status == ExecutionStatus.SUCCESS
        mock_startfile.assert_called_once_with(str(temp_fs))

def test_sys_file_open_adapter_path_not_found():
    adapter = SysFileOpenAdapter()
    
    with patch('os.startfile') as mock_startfile:
        result = adapter.execute("C:\\NonExistentPath\\FakeFolder")
        assert result.status == ExecutionStatus.FAILED
        assert result.error_code == ExecutionErrorCode.PATH_NOT_FOUND
        mock_startfile.assert_not_called()



