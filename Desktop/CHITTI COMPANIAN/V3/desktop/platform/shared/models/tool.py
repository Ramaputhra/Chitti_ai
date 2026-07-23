from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ToolParameter:
    """Parameter definition for a tool."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    choices: Optional[List[str]] = None


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
