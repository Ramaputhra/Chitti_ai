"""
Filesystem Shared Primitive

This module is part of the frozen filesystem infrastructure.
Only functionality proven by at least two capabilities may be added.
Capability-specific logic is prohibited.
"""
import pytest
import shutil
import tempfile
from pathlib import Path

@pytest.fixture
def temp_fs():
    """Provides a temporary filesystem directory for capability testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def populated_fs(temp_fs):
    """Provides a temporary filesystem with some standard files and directories."""
    # Create some dummy files
    (temp_fs / "document.txt").write_text("Hello World")
    (temp_fs / "config.json").write_text('{"key": "value"}')
    
    # Create a dummy folder
    sub_folder = temp_fs / "archive"
    sub_folder.mkdir()
    (sub_folder / "old_doc.txt").write_text("Old stuff")
    
    return temp_fs
