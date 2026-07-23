from dataclasses import dataclass, field
from typing import Dict, Any, Generic, TypeVar, Optional
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class Identity:
    """Base class for all normalized resources (Rule 49)."""
    id: str
    type: str
    display_name: str
    canonical_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class UnknownIdentity(Identity):
    pass

@dataclass(frozen=True)
class WorkspaceIdentity(Identity):
    # Additional semantic aliases mapping to canonical_path
    root: str = ""
    workspace: str = ""
    relative_path: str = ""

@dataclass(frozen=True)
class CommandIdentity(Identity):
    # Metadata includes 'args', 'raw' (redacted)
    category: str = "SYSTEM"

@dataclass(frozen=True)
class ProjectIdentity(Identity):
    project_type: str = "Unknown"
    repository: str = "Unknown"
    language: str = "Unknown"
    build_system: str = "Unknown"

TInput = TypeVar('TInput')
TIdentity = TypeVar('TIdentity', bound=Identity)

class Resolver(ABC, Generic[TInput, TIdentity]):
    """
    Base interface for all deterministic normalizers.
    Providers observe -> Resolvers normalize (Rule 47).
    """
    @abstractmethod
    def resolve(self, input_data: TInput) -> Optional[TIdentity]:
        pass

class ProjectDetector(ABC):
    """
    Interface for ecosystem-specific project identification.
    """
    @abstractmethod
    def detect(self, canonical_path: str) -> Optional[ProjectIdentity]:
        pass
