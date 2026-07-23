from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from desktop.models.knowledge import KnowledgeFact, KnowledgeDocument

class RetrievalStrategy(Enum):
    FACT_ONLY = "FACT_ONLY"
    DOCUMENT_ONLY = "DOCUMENT_ONLY"
    HYBRID = "HYBRID"
    GRAPH_ONLY = "GRAPH_ONLY"
    VECTOR_ONLY = "VECTOR_ONLY"
    FULL_CONTEXT = "FULL_CONTEXT"

@dataclass
class RetrievalQuery:
    """Rich query object to decouple planners from storage mechanisms."""
    text: str = ""
    intent: str = ""
    entities: List[str] = field(default_factory=list)
    language: str = "en"
    workspace: Optional[str] = None
    namespaces: List[str] = field(default_factory=list)
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    max_chunks: int = 10
    token_budget: int = 4000
    include_documents: bool = True
    include_facts: bool = True
    include_memory: bool = True
    include_workspace: bool = True

@dataclass
class RetrievalResult:
    """Standardized output from any RetrievalProvider."""
    provider_id: str
    sources: List[str] = field(default_factory=list)
    facts: List[KnowledgeFact] = field(default_factory=list)
    documents: List[KnowledgeDocument] = field(default_factory=list)
    chunks: List[Any] = field(default_factory=list)
    confidence: float = 1.0
    latency_ms: int = 0
    provider_scores: Dict[str, float] = field(default_factory=dict)
    retrieval_trace: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextPackage:
    """
    Rule 288: Immutable Context.
    Only this package reaches the AI Gateway, never raw chunks.
    """
    conversation_context: List[Any] = field(default_factory=list)
    knowledge_facts: List[KnowledgeFact] = field(default_factory=list)
    workspace: Dict[str, Any] = field(default_factory=dict)
    documents: List[KnowledgeDocument] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    retrieval_metadata: Dict[str, Any] = field(default_factory=dict)
