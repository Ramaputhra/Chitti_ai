import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from desktop.platform.shared.models.provenance import Provenance
from desktop.platform.shared.models.knowledge import FactSource


class MemoryCategory(Enum):
    PREFERENCE = "Preference"
    HABIT = "Habit"
    RELATIONSHIP = "Relationship"
    PROJECT = "Project"
    CONTEXT = "Context"
    TASK = "Task"
    EMOTIONAL = "Emotional"
    PROCEDURAL = "Procedural"


class MemoryStatus(Enum):
    ACTIVE = "Active"
    DORMANT = "Dormant"
    ARCHIVED = "Archived"
    COMPRESSED = "Compressed"
    PRUNED = "Pruned"


@dataclass
class Memory:
    """
    The 4th fundamental object of the CHITTI Platform (alongside ConversationSession, Artifact, Entity).
    Stores subjective significance, meaning, and preferences derived from objective Knowledge.
    """
    content: str
    category: MemoryCategory
    knowledge_ids: List[str] = field(default_factory=list)  # The objective facts this memory is derived from
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: MemoryStatus = MemoryStatus.ACTIVE
    intelligence_score: float = 0.5
    source: FactSource = FactSource.PLANNER
    created_by: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    provenance: Optional[Provenance] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
