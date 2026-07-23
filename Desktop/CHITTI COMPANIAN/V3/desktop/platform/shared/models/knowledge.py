import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from enum import Enum
from desktop.platform.shared.models.provenance import EntityEvidence, Provenance

class FactSource(str, Enum):
    USER = "USER"
    PLANNER = "PLANNER"
    IMPORT = "IMPORT"
    RULE = "RULE"



@dataclass
class KnowledgeEdge:
    source_id: str
    target_id: str
    relationship: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: FactSource = FactSource.PLANNER
    created_by: Optional[str] = None
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)
    provenance: Optional[Provenance] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Entity:
    canonical_name: str
    display_name: str
    entity_type: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aliases: List[str] = field(default_factory=list)
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: Optional[Provenance] = None
    evidence: List[EntityEvidence] = field(default_factory=list)


@dataclass
class KnowledgeSnapshot:
    artifact_ids: List[str] = field(default_factory=list)
    relationship_ids: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
