import unittest
import os
import tempfile
import shutil
from desktop.models.workspace import WorkspaceProfile, WindowPosition
from desktop.runtimes.workspace_runtime import WorkspaceRuntime
from desktop.runtimes.profile_runtime import ProfileRuntime
from desktop.models.profile import UserProfile

class TestPhase7Refinements(unittest.TestCase):
    
    def setUp(self):
        """Create temp directories for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_dir = os.path.join(self.temp_dir, "workspaces")
        self.profile_dir = os.path.join(self.temp_dir, "test_profile")
    
    def tearDown(self):
        """Clean up temp directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workspace_restore(self):
        """
        Workspace Restore
        Workspace -> Open -> Crash -> Restore -> Window Layout identical
        """
        runtime = WorkspaceRuntime(profiles_dir=self.workspace_dir)
        profile = WorkspaceProfile(
            id="ws_dev",
            name="Dev Workspace",
            window_positions={
                "vscode": WindowPosition(x=0, y=0, width=1920, height=1080, maximized=True)
            },
            startup=["vscode"]
        )
        runtime.save_workspace(profile)
        loaded = runtime.get_workspace("ws_dev")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.window_positions["vscode"].width, 1920)
        self.assertTrue(loaded.window_positions["vscode"].maximized)

    def test_user_profile_reload(self):
        """
        User Profile Reload
        Change Voice -> Runtime receives event -> Behavior updates -> No restart required
        """
        # Create test profile directory
        os.makedirs(self.profile_dir, exist_ok=True)
        
        # Create default profile
        runtime = ProfileRuntime(config_dir=self.profile_dir)
        runtime.save_profile() # create default
        
        # Simulating external edit
        import json
        profile_path = os.path.join(self.profile_dir, "profile.json")
        with open(profile_path, "r") as f:
            data = json.load(f)
        data["voice"] = {"preferred_voice": "british_en", "speed": 1.2, "pitch": 1.0, "volume": 1.0}
        with open(profile_path, "w") as f:
            json.dump(data, f)
            
        # Hot reload
        runtime.reload_profile()
        self.assertEqual(runtime.current.voice.preferred_voice, "british_en")
        self.assertEqual(runtime.current.voice.speed, 1.2)

if __name__ == '__main__':
    unittest.main()
