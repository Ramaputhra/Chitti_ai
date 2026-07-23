from dataclasses import dataclass, field
from typing import Any, Dict, List

from desktop.platform.shared.models.tool import ToolDescriptor


@dataclass(frozen=True)
class CapabilityDescriptor:
    name: str
    version: str
    tools: List[ToolDescriptor]
    description: str = ""
    category: str = "general"
    permissions: List[str] = field(default_factory=list)
    health: str = "healthy"
    platform: str = "desktop"
    dependencies: List[str] = field(default_factory=list)
    requires_network: bool = False
    requires_memory: bool = False
    supports_streaming: bool = False
