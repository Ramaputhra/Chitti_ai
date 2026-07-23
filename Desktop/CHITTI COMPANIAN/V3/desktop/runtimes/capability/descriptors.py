from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Dict, Any, Optional

class VerificationSupport(str, Enum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"

@dataclass
class CapabilityDescriptor:
    id: str
    version: str
    permissions: List[str]
    execution_mode: str
    category: str
    action_name: str
    description: str
    examples: List[str] = field(default_factory=list)
    parameters_schema: Dict[str, Any] = field(default_factory=dict)
    verification_support: VerificationSupport = VerificationSupport.SUPPORTED
    verification_reason: Optional[str] = None
    factory: Optional[Callable[[], Any]] = None
