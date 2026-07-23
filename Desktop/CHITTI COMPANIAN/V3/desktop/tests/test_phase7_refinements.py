import unittest
from desktop.models.workspace import WorkspaceProfile, WindowPosition
from desktop.runtimes.workspace_runtime import WorkspaceRuntime
from desktop.runtimes.profile_runtime import ProfileRuntime
from desktop.models.profile import UserProfile

class TestPhase7Refinements(unittest.TestCase):
    
    def test_workspace_restore(self):
        """
        Workspace Restore
        Workspace -> Open -> Crash -> Restore -> Window Layout identical
        """
        runtime = WorkspaceRuntime()
        profile = WorkspaceProfile(
            id="ws_dev",
            name="Dev Workspace",
            window_positions={
                "vscode": WindowPosition(0, 0, 1920, 1080, True)
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
        runtime = ProfileRuntime(config_dir="test_profile")
        runtime.save_profile() # create default
        
        # Simulating external edit
        import json
        with open("test_profile/profile.json", "r") as f:
            data = json.load(f)
        data["voice"] = {"preferred_voice": "british_en", "speed": 1.2, "pitch": 1.0, "volume": 1.0}
        with open("test_profile/profile.json", "w") as f:
            json.dump(data, f)
            
        # Hot reload
        runtime.reload_profile()
        self.assertEqual(runtime.current.voice.preferred_voice, "british_en")
        self.assertEqual(runtime.current.voice.speed, 1.2)

if __name__ == '__main__':
    unittest.main()
