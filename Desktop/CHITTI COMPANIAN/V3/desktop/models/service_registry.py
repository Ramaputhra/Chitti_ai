from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

class ServiceHealth(Enum):
    AVAILABLE = "AVAILABLE"
    LOADING = "LOADING"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"
    DISABLED = "DISABLED"

class ServiceLifecycle(Enum):
    DISCOVERED = "DISCOVERED"
    VALIDATED = "VALIDATED"
    REGISTERED = "REGISTERED"
    READY = "READY"
    DISABLED = "DISABLED"
    REMOVED = "REMOVED"

@dataclass
class ServiceDescriptor:
    """
    Base class for everything executable or discoverable in CHITTI.
    Rule 278: Declarative metadata only.
    """
    id: str
    service_type: str
    name: str
    description: str
    version: str = "1.0.0"
    provider_id: Optional[str] = None
    
    # Sprint 8.5.75: Composition Metadata (Rule 306)
    accepts: List[str] = field(default_factory=list)          # e.g., ["StructuredDocument", "PDF"]
    produces: List[str] = field(default_factory=list)         # e.g., ["Summary", "EmailSent"]
    depends_on: List[str] = field(default_factory=list)       # Strict prerequisites
    optional_followups: List[str] = field(default_factory=list)
    preferred_followups: List[str] = field(default_factory=list)
    
    # Constraints and Scoring
    constraints: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    requires_online: bool = False
    requires_ai: bool = False
    supports_parallel: bool = False
    deterministic: bool = True
    
    # Scoring attributes for Composer
    priority: int = 1
    latency_ms: int = 100
    accuracy_score: float = 1.0
    offline_capable: bool = True
    resource_cost: int = 1
    trust_level: str = "CORE"
    
    manifest_version: str = "1.0"
    api_version: str = "1.0"
    minimum_platform_version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    visibility: str = "PUBLIC"
    health: ServiceHealth = ServiceHealth.AVAILABLE
    lifecycle: ServiceLifecycle = ServiceLifecycle.DISCOVERED
    
    # Cost & Performance metrics
    latency_ms: int = 0
    memory_mb: int = 0
    gpu_required: bool = False
    accuracy_score: float = 1.0
    cost_per_invoke: float = 0.0

    # Constraints
    requires_network: bool = False
    requires_browser: bool = False
    requires_login: bool = False
    requires_authentication: bool = False
    requires_presentation: bool = False
    supports_background: bool = True
    supports_parallel: bool = False


@dataclass
class CapabilityDescriptor(ServiceDescriptor):
    """Describes an atomic executable capability."""
    category: str = "capability"
    supported_inputs: List[str] = field(default_factory=list)
    supported_outputs: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class SkillDescriptor(ServiceDescriptor):
    """
    Describes an orchestrated workflow of capabilities.
    Rule 274: Skills orchestrate, Capabilities execute.
    """
    category: str = "skill"
    required_capabilities: List[str] = field(default_factory=list)
    supported_languages: List[str] = field(default_factory=list)
    knowledge_requirements: List[str] = field(default_factory=list)
    presentation_support: bool = False
    execution_graph_id: str = "" # Reference to the versioned graph


@dataclass
class ProviderDescriptor(ServiceDescriptor):
    """Describes a data, knowledge, or AI provider."""
    category: str = "provider"
    provider_type: str = ""
    namespaces: List[str] = field(default_factory=list)


@dataclass
class ServiceQuery:
    """Deterministic query for the Planner to discover services (Rule 277)."""
    intent: str = ""
    input_type: str = ""
    output_type: str = ""
    resources: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    language: str = "en"
    offline_only: bool = False
    requires_gpu: bool = False
    max_latency_ms: Optional[int] = None
    tags: List[str] = field(default_factory=list)
