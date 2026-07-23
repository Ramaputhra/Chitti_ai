from abc import ABC, abstractmethod
from typing import List, Optional
from desktop.models.knowledge import KnowledgeFact, KnowledgeQuery, KnowledgeRelationship, KnowledgeDocument

class IKnowledgeRepository(ABC):
    """
    Abstract interface for Knowledge storage.
    Hides the underlying implementation (SQLite/PostgreSQL) from the Knowledge Runtime.
    """
    
    @abstractmethod
    def store_fact(self, fact: KnowledgeFact) -> bool:
        pass

    @abstractmethod
    def get_fact(self, fact_id: str) -> Optional[KnowledgeFact]:
        pass

    @abstractmethod
    def update_fact(self, fact: KnowledgeFact) -> bool:
        """Rule 267 implies updates should just append/supersede, but repository handles the physical write."""
        pass

    @abstractmethod
    def query_facts(self, query: KnowledgeQuery) -> List[KnowledgeFact]:
        pass

    @abstractmethod
    def store_relationship(self, relationship: KnowledgeRelationship) -> bool:
        pass

    @abstractmethod
    def store_document(self, document: KnowledgeDocument) -> bool:
        pass
