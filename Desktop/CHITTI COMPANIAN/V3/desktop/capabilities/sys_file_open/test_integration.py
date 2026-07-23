import os
import unittest
from desktop.capabilities.sys_file_open.adapter import SysFileOpenAdapter

class TestSysFileOpenIntegration(unittest.TestCase):
    """
    Requirement 7: End-to-End Integration Test
    Verifies that the adapter executes correctly without invoking the full cognitive pipeline.
    """
    def test_open_valid_path(self):
        adapter = SysFileOpenAdapter()
        # Should return True and asynchronously open the process
        # We use a safe known path (the current directory)
        result = adapter.execute(os.getcwd())
        self.assertTrue(result)

    def test_open_invalid_path(self):
        adapter = SysFileOpenAdapter()
        # Should return False gracefully (Failure Policy: non-recoverable path_not_found)
        result = adapter.execute("C:/This/Path/Does/Not/Exist_12345")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
