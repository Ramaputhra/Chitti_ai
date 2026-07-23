import pytest
from desktop.models.execution import ExecutionStatus, ExecutionErrorCode
from desktop.capabilities.sys.file.compress.adapter import SysFileCompressAdapter

def test_compress_adapter_missing_params():
    adapter = SysFileCompressAdapter()
    res = adapter.execute(sources=[], destination_dir="dest", archive_name="archive")
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.MISSING_REQUIRED_PARAMETER

def test_compress_adapter_missing_source(temp_fs):
    adapter = SysFileCompressAdapter()
    res = adapter.execute(
        sources=[str(temp_fs / "does_not_exist.txt")], 
        destination_dir=str(temp_fs), 
        archive_name="archive"
    )
    assert res.status == ExecutionStatus.FAILED
    assert res.error_code == ExecutionErrorCode.SOURCE_NOT_FOUND

def test_compress_adapter_zip_success(temp_fs):
    adapter = SysFileCompressAdapter()
    
    src1 = temp_fs / "file1.txt"
    src1.write_text("hello")
    src2 = temp_fs / "file2.txt"
    src2.write_text("world")
    
    res = adapter.execute(
        sources=[str(src1), str(src2)], 
        destination_dir=str(temp_fs), 
        archive_name="archive",
        format="zip"
    )
    assert res.status == ExecutionStatus.SUCCESS
    assert res.output_data["count"] == 1
    
    archive_path = temp_fs / "archive.zip"
    assert archive_path.exists()
    assert res.output_data["results"][0]["path"] == str(archive_path)

def test_compress_adapter_tar_success(temp_fs):
    adapter = SysFileCompressAdapter()
    
    src1 = temp_fs / "file1.txt"
    src1.write_text("hello")
    
    res = adapter.execute(
        sources=[str(src1)], 
        destination_dir=str(temp_fs), 
        archive_name="archive",
        format="tar"
    )
    assert res.status == ExecutionStatus.SUCCESS
    assert res.output_data["count"] == 1
    
    archive_path = temp_fs / "archive.tar"
    assert archive_path.exists()

def test_compress_adapter_collision(temp_fs):
    adapter = SysFileCompressAdapter()
    
    src1 = temp_fs / "file1.txt"
    src1.write_text("hello")
    
    # Create conflicting archive
    archive_path = temp_fs / "archive.zip"
    archive_path.write_text("garbage")
    
    # Test fail policy
    res1 = adapter.execute(
        sources=[str(src1)], 
        destination_dir=str(temp_fs), 
        archive_name="archive",
        format="zip",
        collision_policy="fail"
    )
    assert res1.status == ExecutionStatus.FAILED
    assert res1.error_code == ExecutionErrorCode.FILE_ALREADY_EXISTS
    
    # Test overwrite policy
    res2 = adapter.execute(
        sources=[str(src1)], 
        destination_dir=str(temp_fs), 
        archive_name="archive",
        format="zip",
        collision_policy="overwrite"
    )
    assert res2.status == ExecutionStatus.SUCCESS
