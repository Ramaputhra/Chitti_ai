from dataclasses import dataclass
from typing import List, Dict, Any

# =====================================================================
# Domain Payloads for the AI Runtime
# =====================================================================

@dataclass
class IntentClassification:
    intent: str
    confidence: float
    entities: Dict[str, Any]

@dataclass
class EntityExtraction:
    entities: Dict[str, str]

@dataclass
class PresentationSelection:
    template_id: str
    reasoning: str

@dataclass
class Transcript:
    text: str
    language: str
    timestamps: List[Dict[str, Any]]  # e.g., [{"start": 0.0, "end": 2.5, "text": "hello"}]

@dataclass
class WakeEvent:
    detected: bool
    score: float

@dataclass
class Vector:
    embedding: List[float]

@dataclass
class MemoryResult:
    memory_id: str
    content: str
    similarity: float

@dataclass
class ImportanceScore:
    score: float
    category: str  # e.g., "long_term", "temporary"

@dataclass
class VisionDescription:
    objects: List[str]
    text: str
    ui_elements: List[Dict[str, Any]]

@dataclass
class ExecutionPlan:
    steps: List[Dict[str, Any]]
    estimated_cost: float
    dependencies: List[str]
