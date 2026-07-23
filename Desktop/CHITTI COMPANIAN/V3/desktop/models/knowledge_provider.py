from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from desktop.models.knowledge import KnowledgeFact, KnowledgeNamespace, KnowledgeRelationship, KnowledgeDocument, KnowledgeConflict

class KnowledgeCollectionTrigger(Enum):
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    USER_LOGIN = "USER_LOGIN"
    WORKSPACE_OPENED = "WORKSPACE_OPENED"
    DOCUMENT_IMPORTED = "DOCUMENT_IMPORTED"
    MEMORY_UPDATED = "MEMORY_UPDATED"
    PROFILE_CHANGED = "PROFILE_CHANGED"
    SETTINGS_CHANGED = "SETTINGS_CHANGED"
    MANUAL_REFRESH = "MANUAL_REFRESH"
    SCHEDULED_REFRESH = "SCHEDULED_REFRESH"

class RefreshPolicy(Enum):
    EVENT = "EVENT"
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    HYBRID = "HYBRID"

@dataclass
class KnowledgeProviderDescriptor:
    provider_id: str
    name: str
    version: str
    namespaces: List[KnowledgeNamespace]
    priority: int
    refresh_policy: RefreshPolicy
    supports_manual_refresh: bool
    supports_incremental: bool

@dataclass
class KnowledgeCollectionResult:
    facts: List[KnowledgeFact] = field(default_factory=list)
    documents: List[KnowledgeDocument] = field(default_factory=list)
    relationships: List[KnowledgeRelationship] = field(default_factory=list)
    conflicts: List[KnowledgeConflict] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

class IKnowledgeProvider(ABC):
    """
    Rule 271: Knowledge Providers are pure collectors.
    They normalize external information into Knowledge models but never validate,
    persist, infer, or publish knowledge independently.
    """
    
    @abstractmethod
    def descriptor(self) -> KnowledgeProviderDescriptor:
        pass

    @abstractmethod
    async def collect(self, trigger: KnowledgeCollectionTrigger) -> KnowledgeCollectionResult:
        """
        Collects facts, documents, and relationships. 
        Rule 272: Always initiated by Knowledge Runtime.
        """
        pass

    @abstractmethod
    async def refresh(self) -> None:
        """Forces a manual or scheduled refresh of the provider's internal state."""
        pass
