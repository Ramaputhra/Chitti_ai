from enum import Enum
from typing import List, Protocol


class ResourceType(Enum):
    MODEL = "MODEL"
    ICON = "ICON"
    THEME = "THEME"
    PLUGIN = "PLUGIN"
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"
    TEMP = "TEMP"


class IResourceManager(Protocol):
    """
    Manages physical files and assets across the application.
    Abstracts direct OS paths from domain logic.
    """
    def initialize(self) -> None:
        ...

    def get_path(self, resource_type: ResourceType, filename: str) -> str:
        """Returns the absolute path for a given resource."""
        ...

    def list_resources(self, resource_type: ResourceType) -> List[str]:
        """Lists all files available for a given resource type."""
        ...

    def clear_temp(self) -> None:
        """Wipes the temporary resources directory."""
        ...
