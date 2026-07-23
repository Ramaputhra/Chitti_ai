import pytest
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.search.adapter import SysFileSearchAdapter

def test_sys_file_search_missing_location():
    adapter = SysFileSearchAdapter()
    res = adapter.execute(location="")
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.MISSING_REQUIRED_PARAMETER

def test_sys_file_search_basic(temp_fs):
    adapter = SysFileSearchAdapter()
    
    # Create some files
    (temp_fs / "file1.txt").write_text("hello")
    (temp_fs / "file2.pdf").write_text("hello world")
    
    dir1 = temp_fs / "docs"
    dir1.mkdir()
    (dir1 / "file3.txt").write_text("deep")
    
    # Search all
    res = adapter.execute(location=str(temp_fs), query="*")
    assert res.status == ExecutionStatus.SUCCESS
    assert len(res.output_data["results"]) == 3
    
def test_sys_file_search_extension_filter(temp_fs):
    adapter = SysFileSearchAdapter()
    
    (temp_fs / "file1.txt").write_text("hello")
    (temp_fs / "file2.pdf").write_text("hello world")
    
    res = adapter.execute(location=str(temp_fs), file_types=["pdf", ".png"])
    assert res.status == ExecutionStatus.SUCCESS
    assert len(res.output_data["results"]) == 1
    assert res.output_data["results"][0]["extension"] == ".pdf"

def test_sys_file_search_size_filter(temp_fs):
    adapter = SysFileSearchAdapter()
    
    (temp_fs / "small.txt").write_text("1") # 1 byte
    (temp_fs / "large.txt").write_text("1234567890") # 10 bytes
    
    res = adapter.execute(location=str(temp_fs), min_size=5)
    assert res.status == ExecutionStatus.SUCCESS
    assert len(res.output_data["results"]) == 1
    assert res.output_data["results"][0]["name"] == "large.txt"

def test_sys_file_search_include_directories(temp_fs):
    adapter = SysFileSearchAdapter()
    
    dir1 = temp_fs / "photos"
    dir1.mkdir()
    (dir1 / "pic.jpg").write_text("data")
    
    res = adapter.execute(location=str(temp_fs), query="photos", include_directories=True)
    assert res.status == ExecutionStatus.SUCCESS
    assert len(res.output_data["results"]) == 1
    assert res.output_data["results"][0]["is_directory"] == True
