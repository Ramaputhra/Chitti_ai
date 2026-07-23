from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List, Type, Optional, Dict, Any
from enum import Enum
from desktop.runtimes.capability.context import CapabilityContext
from desktop.platform.shared.models.execution import ExecutionResult, ExecutionStatus

# Re-export ExecutionResult and ExecutionStatus for convenience
__all__ = ['ICapability', 'CapabilityDescriptor', 'ICapabilityRegistry', 'SimpleCapabilityRegistry', 'CapabilityCatalog', 'ExecutionResult', 'ExecutionStatus']


class CapabilityExecutionMode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"
    BACKGROUND = "background"
    ISOLATED = "isolated"


class ICapability(ABC):
    """
    Rule 178: Capabilities are the only units of execution.
    """
    @property
    @abstractmethod
    def capability_id(self) -> str:
        """Unique identifier for the capability."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the capability."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the capability."""
        pass
    
    @abstractmethod
    async def execute(self, context: CapabilityContext) -> ExecutionResult:
        """Execute the capability using the provided immutable context."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the capability gracefully."""
        pass


@dataclass
class CapabilityDescriptor:
    """
    Describes a capability for the registry without instantiating it.
    Enables versioning, permissions, and discovery.
    """
    id: str
    version: str
    permissions: List[str]
    execution_mode: CapabilityExecutionMode
    factory: Callable[[], ICapability]
    # Semantic Metadata for Catalog Generation
    category: str = "Uncategorized"
    action_name: str = ""
    description: str = ""
    parameters_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    
    def create_instance(self) -> ICapability:
        """Create an instance of the capability using the factory."""
        return self.factory()

class ICapabilityRegistry(ABC):
    """
    Registry to map action strings to CapabilityDescriptors.
    """
    @abstractmethod
    def register(self, descriptor: CapabilityDescriptor) -> None:
        pass

    @abstractmethod
    def resolve(self, action: str) -> Optional[CapabilityDescriptor]:
        pass

    @abstractmethod
    def resolve_by_action_name(self, action_name: str) -> Optional[CapabilityDescriptor]:
        pass

class SimpleCapabilityRegistry(ICapabilityRegistry):
    def __init__(self):
        self._capabilities = {}
        
    def register(self, descriptor: CapabilityDescriptor) -> None:
        self._capabilities[descriptor.id] = descriptor
        
    def resolve(self, action: str) -> Optional[CapabilityDescriptor]:
        return self._capabilities.get(action)

    def resolve_by_action_name(self, action_name: str) -> Optional[CapabilityDescriptor]:
        for desc in self._capabilities.values():
            if desc.action_name == action_name:
                return desc
        return None

class CapabilityCatalog:
    """
    Exposes high-level capability domains and summaries to AIRuntime
    without inflating the prompt. Assists PlannerRuntime with resolution.
    """
    def __init__(self, registry: ICapabilityRegistry):
        self.registry = registry

    def generate_summary(self) -> str:
        if not hasattr(self.registry, '_capabilities'):
            return "No capabilities registered."
            
        categories = {}
        for desc in self.registry._capabilities.values():
            # Skip capabilities without an action_name (un-annotated stubs)
            if not desc.action_name: continue
            
            cat = desc.category or "Uncategorized"
            if cat not in categories:
                categories[cat] = []
            
            # Compact format: action(params) - description
            params_str = ", ".join([f"{k}:{v}" for k,v in desc.parameters_schema.items()])
            action_desc = f"{desc.action_name}({params_str}) - {desc.description}"
            if desc.examples:
                action_desc += f" (Ex: {desc.examples[0]})"
            categories[cat].append(action_desc)
            
        summary_lines = ["Capability Summary (Use appropriate Intent + set `action` parameter):"]
        for cat, actions in sorted(categories.items()):
            summary_lines.append(f"Domain: {cat}")
            for a in sorted(actions):
                summary_lines.append(f"  - {a}")
        return "\n".join(summary_lines)

    def resolve_action(self, category: Optional[str], action_name: str) -> Optional[CapabilityDescriptor]:
        if not hasattr(self.registry, '_capabilities') or not action_name:
            return None
        for desc in self.registry._capabilities.values():
            cat_match = (desc.category.lower() == category.lower()) if (category and desc.category) else True
            if cat_match and desc.action_name.lower() == action_name.lower():
                return desc
            # Fallback exact ID match
            if desc.id == action_name:
                return desc
        return None
