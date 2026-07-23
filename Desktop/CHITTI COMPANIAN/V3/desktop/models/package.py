from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

class PackageLifecycle(Enum):
    DISCOVERED = "DISCOVERED"
    DOWNLOADED = "DOWNLOADED"
    VERIFIED = "VERIFIED"
    INSTALLED = "INSTALLED"
    REGISTERED = "REGISTERED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    REMOVED = "REMOVED"

class UpdatePolicy(Enum):
    MANUAL = "MANUAL"
    SECURITY_ONLY = "SECURITY_ONLY"
    STABLE = "STABLE"
    BETA = "BETA"
    NIGHTLY = "NIGHTLY"

class ComponentType(Enum):
    """
    Rule 313: Defines which runtime owns this component.
    """
    CAPABILITY = "CAPABILITY"
    PRESENTATION_TEMPLATE = "PRESENTATION_TEMPLATE"
    THEME = "THEME"
    VOICE = "VOICE"
    KNOWLEDGE = "KNOWLEDGE"
    EXPERIENCE = "EXPERIENCE"
    WORKSPACE_PROFILE = "WORKSPACE_PROFILE"
    REASONING_POLICY = "REASONING_POLICY"
    MODEL = "MODEL"

@dataclass
class PackageComponent:
    """
    A single component packed inside a PackageManifest.
    """
    id: str
    type: ComponentType
    entrypoint: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PackageManifest:
    """
    Universal distribution schema for any CHITTI feature package.
    """
    id: str
    version: str
    type: str # High-level descriptor e.g. "SKILL", "PLUGIN", "THEME_PACK"
    publisher: str
    description: str
    
    # Internal components to be unpacked and routed
    components: List[PackageComponent] = field(default_factory=list)
    
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    
    checksum: str = ""
    signature: str = ""
    license: str = ""
    homepage: str = ""
    size_bytes: int = 0
    update_channel: UpdatePolicy = UpdatePolicy.STABLE
    rollback_version: Optional[str] = None
    
    platform_min_version: str = "1.0.0"
    platform_max_version: Optional[str] = None

@dataclass
class PackageBundle:
    """
    An installer manifest that groups multiple packages together.
    """
    bundle_id: str
    name: str
    description: str
    minimum_platform_version: str = "1.0.0"
    
    required_packages: List[str] = field(default_factory=list)
    optional_packages: List[str] = field(default_factory=list)
