from typing import Dict, Protocol


class IVersionManager(Protocol):
    """
    Interface for the CHITTI Version Manager.
    Exposes immutable version and runtime environment data.
    """

    def initialize(self) -> None:
        """Initializes the manager and logs the startup banner."""
        ...

    def version(self) -> str:
        """Returns the application version."""
        ...

    def architecture(self) -> str:
        """Returns the architecture version."""
        ...

    def build(self) -> str:
        """Returns the build number."""
        ...

    def git_commit(self) -> str:
        """Returns the current git commit hash."""
        ...

    def git_branch(self) -> str:
        """Returns the current git branch."""
        ...

    def runtime(self) -> str:
        """Returns the Python runtime version."""
        ...

    def environment(self) -> str:
        """Returns the deployment environment (e.g., Development)."""
        ...

    def summary(self) -> Dict[str, str]:
        """Returns a summary dictionary of all version info."""
        ...
