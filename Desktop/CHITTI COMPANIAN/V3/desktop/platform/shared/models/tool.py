from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ToolDescriptor:
    name: str
    description: str
    parameters: Dict[str, Any]
    examples: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    timeout: float = 30.0
    category: str = "general"
    version: str = "1.0.0"
