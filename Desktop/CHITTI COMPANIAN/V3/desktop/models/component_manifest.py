from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ComponentPerformance:
    cpu_latency_ms: Optional[float] = None
    gpu_latency_ms: Optional[float] = None
    ram_mb: Optional[int] = None
    vram_mb: Optional[int] = None

@dataclass
class CapabilityRequirements:
    requires: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)

@dataclass
class ComponentManifest:
    """
    Typed representation of a Component YAML manifest.
    Describes the identity, dependencies, capabilities, and performance
    profile of an external component (e.g., an AI Model or Plugin).
    """
    component_id: str
    component_type: str  # e.g., 'ai_model', 'voice', 'plugin'
    version: str
    provider_backend: str
    runtime: str
    
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    
    performance: Optional[ComponentPerformance] = None
    supported_devices: List[str] = field(default_factory=lambda: ["cpu"])
    
    # Optional fields for models
    quantizations: List[str] = field(default_factory=list)
    license: Optional[str] = None
    download_url: Optional[str] = None
    checksum: Optional[str] = None
