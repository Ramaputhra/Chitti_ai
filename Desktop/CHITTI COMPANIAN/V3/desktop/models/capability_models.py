from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class VerificationManifest:
    required: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    fallback: List[str] = field(default_factory=list)
    timeout_seconds: float = 5.0
    minimum_confidence: float = 0.95
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CapabilityManifest:
    id: str
    name: str
    description: str
    version: str
    category: str
    
    # Semantic tags for resolution
    actions: List[str] = field(default_factory=list)
    objects: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    
    # Execution contract
    required_parameters: List[str] = field(default_factory=list)
    optional_parameters: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    timeout: float = 10.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    
    supports_learning: bool = True
    
    # Separate verification concern
    verification: Optional[VerificationManifest] = None
