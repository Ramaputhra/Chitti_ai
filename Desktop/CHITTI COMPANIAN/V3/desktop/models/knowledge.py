from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time

class KnowledgeSource(Enum):
    USER = "USER"
    DOCUMENT = "DOCUMENT"
    PROJECT = "PROJECT"
    SYSTEM = "SYSTEM"
    MEMORY = "MEMORY"
    LLM = "LLM"
    API = "API"
    PLUGIN = "PLUGIN"

class KnowledgeLifecycle(Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    STORED = "STORED"
    INDEXED = "INDEXED"
    EMBEDDED = "EMBEDDED"
    LINKED = "LINKED"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"

class KnowledgeNamespace(Enum):
    SYSTEM = "system"
    USER = "user"
    WORKSPACE = "workspace"
    PLUGINS = "plugins"
    GITHUB = "github"
    CALENDAR = "calendar"
    EMAIL = "email"

@dataclass
class KnowledgeFact:
    """Graph-triple representing a distinct piece of explicit knowledge."""
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float
    source: KnowledgeSource
    namespace: KnowledgeNamespace
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    scope: str = "global"
    importance: int = 1
    tags: List[str] = field(default_factory=list)
    version: int = 1
    lifecycle: KnowledgeLifecycle = KnowledgeLifecycle.CREATED
    fact_root_id: str = "" # Associates all versions of a fact logically
    supersedes_id: Optional[str] = None # For version history


@dataclass
class KnowledgeRelationship:
    """Explicit connections between facts to build a richer Knowledge Graph."""
    id: str
    from_fact: str
    to_fact: str
    relationship_type: str
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)

@dataclass
class KnowledgeDocument:
    """Tracks raw documents to support RAG pipelines."""
    id: str
    title: str
    path: str
    project: str
    checksum: str
    chunks: int = 0
    embedding_status: str = "PENDING"
    chunk_count: int = 0
    last_indexed: float = 0.0
    embedding_model: str = ""
    embedding_version: str = ""
    indexed_at: float = 0.0

@dataclass
class KnowledgeProject:
    """Hierarchical container for knowledge contexts."""
    id: str
    name: str
    parent_id: Optional[str] = None

@dataclass
class KnowledgeCollection:
    """Arbitrary grouping of knowledge."""
    id: str
    name: str

@dataclass
class KnowledgeQuery:
    """A deterministic, expressive query for the Knowledge Runtime."""
    text: str = ""
    entities: List[str] = field(default_factory=list)
    scope: str = ""
    project: str = ""
    collection: str = ""
    namespace: Optional[KnowledgeNamespace] = None
    tags: List[str] = field(default_factory=list)
    max_results: int = 10
    minimum_confidence: float = 0.5
    include_history: bool = False
    latest_only: bool = True

class KnowledgeResolutionStrategy(Enum):
    CREATE_NEW_VERSION = "CREATE_NEW_VERSION"
    KEEP_EXISTING = "KEEP_EXISTING"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    REJECT = "REJECT"

@dataclass
class KnowledgeConflict:
    """Represents a conflict between an existing fact and an incoming fact."""
    existing_fact: KnowledgeFact
    incoming_fact: KnowledgeFact
    reason: str
    resolution: KnowledgeResolutionStrategy = KnowledgeResolutionStrategy.MANUAL_REVIEW
