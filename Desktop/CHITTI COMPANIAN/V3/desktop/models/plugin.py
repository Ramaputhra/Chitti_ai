from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

class PluginPermission(Enum):
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    DESKTOP_AUTOMATION = "desktop.automation"
    INTERNET = "internet"
    CLIPBOARD = "clipboard"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    NOTIFICATIONS = "notifications"
    PRESENTATION = "presentation"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"

class TrustLevel(Enum):
    CORE = "CORE"
    TRUSTED = "TRUSTED"
    VERIFIED = "VERIFIED"
    COMMUNITY = "COMMUNITY"
    DEVELOPMENT = "DEVELOPMENT"
    UNSAFE = "UNSAFE"

class PluginLifecycle(Enum):
    DISCOVERED = "DISCOVERED"
    VERIFIED = "VERIFIED"
    VALIDATED = "VALIDATED"
    LOADED = "LOADED"
    REGISTERED = "REGISTERED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UNLOADED = "UNLOADED"
    REMOVED = "REMOVED"

class PluginHealth(Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    BROKEN = "BROKEN"
    DISABLED = "DISABLED"
    CRASHED = "CRASHED"
    UPDATING = "UPDATING"

@dataclass
class PluginResourceLimits:
    cpu_percent: int = 100
    ram_mb: int = 512
    timeout_ms: int = 30000
    max_threads: int = 4
    gpu_access: bool = False
    network_access: bool = False

@dataclass
class PluginManifest:
    plugin_id: str
    version: str
    author: str
    platform_api_version: str # e.g. "1.2"
    minimum_platform_version: str # e.g. "1.0.0"
    maximum_platform_version: Optional[str] = None
    permissions: List[PluginPermission] = field(default_factory=list)
    resource_limits: PluginResourceLimits = field(default_factory=PluginResourceLimits)
    provides: List[str] = field(default_factory=list) # List of class names or descriptors
    requires: List[str] = field(default_factory=list) # Dependencies
    trust_level: TrustLevel = TrustLevel.UNSAFE
    signature_checksum: str = ""
    signature_publisher: str = ""

@dataclass
class PluginContext:
    """
    Passed to plugin execution routines instead of relying on globals.
    Rule 285: Plugins are stateless between invocations.
    """
    plugin_id: str
    version: str
    trust_level: TrustLevel
    permissions: List[PluginPermission]
    resource_limits: PluginResourceLimits
    execution_id: str
    trace_id: str
    timeout_ms: int
    locale: str = "en-US"
    user_profile: Dict[str, Any] = field(default_factory=dict)
    platform_version: str = "1.0.0"
