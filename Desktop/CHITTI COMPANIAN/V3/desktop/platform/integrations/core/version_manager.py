import os
import platform
from typing import Dict

from desktop.platform.configuration.application import AppInfo
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.version import IVersionManager


class VersionManager(IVersionManager):
    """
    Manages application version, architecture version, and runtime environment.
    
    Service Lifecycle:
    - Created by: Application Bootstrap
    - Owned by: ApplicationContext
    - Used by: Logging, Health, UI, OTA Services
    - Destroyed by: Lifecycle Manager
    """

    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._env = os.environ.get("CHITTI_ENV", "Development")
        self._build = "0001"
        self._commit = "unknown"
        self._branch = "develop"
        # Note: In a CI/CD pipeline, build, commit, and branch 
        # would be injected from a build artifact or injected file.

    def initialize(self) -> None:
        banner = (
            "\n" + "=" * 40 + "\n"
            f"{AppInfo.NAME}\n"
            f"Version: {self.version()}\n"
            f"Architecture: {self.architecture()}\n"
            f"Build: {self.build()}\n"
            f"Branch: {self.git_branch()}\n"
            f"Python: {self.runtime()}\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"Environment: {self.environment()}\n"
            + "=" * 40
        )
        self.logger.info(banner)

    def version(self) -> str:
        return AppInfo.VERSION

    def architecture(self) -> str:
        return AppInfo.ARCHITECTURE_VERSION

    def build(self) -> str:
        return self._build

    def git_commit(self) -> str:
        return self._commit

    def git_branch(self) -> str:
        return self._branch

    def runtime(self) -> str:
        return platform.python_version()

    def environment(self) -> str:
        return self._env

    def summary(self) -> Dict[str, str]:
        return {
            "version": self.version(),
            "architecture": self.architecture(),
            "build": self.build(),
            "branch": self.git_branch(),
            "python": self.runtime(),
            "os": f"{platform.system()} {platform.release()}",
            "environment": self.environment(),
        }
