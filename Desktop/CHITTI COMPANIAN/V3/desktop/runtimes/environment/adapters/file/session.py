from dataclasses import dataclass, field
from typing import Dict, List, Any
from desktop.models.environment import EnvironmentSession

@dataclass
class FileSession(EnvironmentSession):
    """
    Session context for file operations, preparing for streaming and long-running workflows.
    """
    working_root: str = ""
    mounted_resources: Dict[str, str] = field(default_factory=dict)
    opened_resources: List[str] = field(default_factory=list)
    watch_subscriptions: Dict[str, Any] = field(default_factory=dict)
    temporary_resources: List[str] = field(default_factory=list)
