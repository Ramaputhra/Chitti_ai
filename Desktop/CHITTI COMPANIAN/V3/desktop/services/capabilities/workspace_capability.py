import os
import glob
import subprocess
import webbrowser
import yaml
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor


class WorkspaceCapability(ICapability):
    """
    Manages Workspace Profiles, enabling CHITTI to setup or teardown app layouts.
    """
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        
        local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
        self.profiles_dir = os.path.join(local_app_data, "CHITTI", "profiles")

    @property
    def name(self) -> str:
        return "WorkspaceCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        if not os.path.exists(self.profiles_dir):
            try:
                os.makedirs(self.profiles_dir, exist_ok=True)
                self.logger.info(f"Created default profiles directory at {self.profiles_dir}")
                # Create default profile
                self._create_default_profile()
            except Exception as e:
                self.logger.warning(f"Failed to create profiles directory: {e}")
                self._state = ServiceState.ERROR
                return
                
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"profiles_dir_exists": os.path.exists(self.profiles_dir)}

    def execute(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "restore_profile":
            return self.restore_profile(parameters.get("profile", ""))
        elif action == "list_profiles":
            return self.list_profiles()
        elif action == "load_profile":
            return self.load_profile(parameters.get("profile", ""))
        raise NotImplementedError(f"Action {action} not supported by {self.name}")

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Manage and restore workspace profiles (apps, urls, folders).",
            actions=["restore_profile", "list_profiles", "load_profile", "save_profile", "delete_profile"],
        )

    def _create_default_profile(self):
        default = {
            "name": "Writing",
            "description": "Default writing workspace",
            "apps": ["notepad"],
            "urls": ["https://mail.google.com"],
            "documents": [],
            "folders": [],
            "commands": [],
            "voice": "Writing workspace is ready."
        }
        self.save_profile("writing", default)

    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        path = os.path.join(self.profiles_dir, f"{profile_name.lower()}.yaml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Profile {profile_name} not found.")
            
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_profile(self, profile_name: str, config: Dict[str, Any]) -> None:
        path = os.path.join(self.profiles_dir, f"{profile_name.lower()}.yaml")
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)

    def list_profiles(self) -> List[str]:
        profiles = []
        for file in glob.glob(os.path.join(self.profiles_dir, "*.yaml")):
            profiles.append(os.path.basename(file).replace(".yaml", ""))
        return profiles

    def restore_profile(self, profile_name: str) -> str:
        """
        Launches apps, URLs, and folders specified in the profile.
        Returns the voice confirmation text if specified.
        """
        try:
            profile = self.load_profile(profile_name)
        except Exception as e:
            self.logger.error(f"Failed to load profile {profile_name}: {e}")
            return f"I couldn't find the {profile_name} workspace."

        self.logger.info(f"Restoring workspace profile: {profile_name}")

        for url in profile.get("urls", []):
            try:
                webbrowser.open(url)
            except Exception as e:
                self.logger.warning(f"Failed to open URL {url}: {e}")

        for folder in profile.get("folders", []):
            try:
                # On Windows, os.startfile opens the folder
                os.startfile(folder)
            except Exception as e:
                self.logger.warning(f"Failed to open folder {folder}: {e}")

        for app in profile.get("apps", []):
            try:
                # Basic launch (assumes app is in PATH or registered)
                subprocess.Popen(app, shell=True)
            except Exception as e:
                self.logger.warning(f"Failed to launch app {app}: {e}")

        for doc in profile.get("documents", []):
            try:
                os.startfile(doc)
            except Exception as e:
                self.logger.warning(f"Failed to open document {doc}: {e}")

        for cmd in profile.get("commands", []):
            try:
                subprocess.Popen(cmd, shell=True)
            except Exception as e:
                self.logger.warning(f"Failed to run command {cmd}: {e}")

        return profile.get("voice", f"{profile.get('name', profile_name)} workspace is ready.")
