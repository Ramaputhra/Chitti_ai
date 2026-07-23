from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class KnowledgeScope(Enum):
    CURRENT_CONTEXT = 1
    LOCAL_MEMORY = 2
    ORGANIZATION = 3
    GLOBAL = 4

class RetrievalStrategy(Enum):
    SEMANTIC = 1
    GRAPH = 2
    TIMELINE = 3
    ENTITY = 4
    HYBRID = 5

class KnowledgePerspective(Enum):
    CHRONOLOGICAL = 1
    ARCHITECTURAL = 2
    DECISION = 3
    PEOPLE = 4
    PROJECT = 5
    CONCEPTUAL = 6

@dataclass
class KnowledgeQuery:
    intent: str # Explain, Recall, Compare, Timeline, etc.
    scope: KnowledgeScope
    entities: List[str]
    time_window: str
    confidence_required: float
    output_format: str
    traceability: str
    constraints: List[str]

@dataclass
class MemoryGraph:
    """Ephemeral working memory representation."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    source_artifacts: List[str]

@dataclass
class KnowledgeConfidence:
    coverage: float
    agreement: float
    freshness: str
    traceability: float

@dataclass
class SynthesisArtifact:
    """The standard response model for Knowledge Access."""
    title: str
    summary: str
    sections: Dict[str, str]
    citations: List[str]
    confidence: KnowledgeConfidence
    retrieved_facts: List[str]   # Rule 155
    inferred_conclusions: List[str] # Rule 155
    unresolved_gaps: List[str]   # Rule 155
    followup_questions: List[str]
    generated_from: str

@dataclass
class KnowledgeSession:
    """Conversation state for multi-turn exploration."""
    original_query: KnowledgeQuery
    retrieval_context: str
    followup_history: List[str]
    active_memory_graph: MemoryGraph
