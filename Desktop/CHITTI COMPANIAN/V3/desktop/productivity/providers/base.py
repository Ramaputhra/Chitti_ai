from abc import ABC, abstractmethod
from desktop.models.session import WorkSession
from desktop.models.evidence import ProviderEvidence, EvidenceDomain

from dataclasses import dataclass

@dataclass
class ProviderCapabilities:
    supports_realtime: bool = False
    supports_history: bool = False
    supports_restore: bool = False
    supports_statistics: bool = False
    supports_background_processing: bool = False

class ContextProvider(ABC):
    """
    Base class for all Context Providers (e.g. Browser, Clipboard, Explorer).
    Providers are responsible for extracting raw deterministic evidence and returning
    ProviderEvidence (clusters and redundancies).
    They must never interpret semantic meaning or write to Memory.
    """
    
    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Declares the introspective capabilities of this provider"""
        pass
        
    @property
    @abstractmethod
    def domain(self) -> EvidenceDomain:
        """Declares the primary cognitive domain of this provider (Rule 51)"""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the provider (e.g. 'BrowserProvider')"""
        pass
        
    @abstractmethod
    def build_evidence(self, session: WorkSession) -> ProviderEvidence:
        """
        Extract deterministic evidence from the given session, grouping it into
        EvidenceClusters and RedundantEvidence.
        """
        pass
