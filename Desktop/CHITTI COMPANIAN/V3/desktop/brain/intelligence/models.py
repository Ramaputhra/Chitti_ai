from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass(frozen=True)
class ExplainabilityTrace:
    contributing_artifacts: List[str] = field(default_factory=list)
    topological_paths: List[str] = field(default_factory=list)
    root_episodes: List[str] = field(default_factory=list)
    conflict_overrides: List[str] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class IntelligenceResult:
    primary_insight: str
    confidence_score: float
    trace: ExplainabilityTrace
    rejected: bool = False

@dataclass(frozen=True)
class IntelligenceQuery:
    query_intent: str
    active_context: Dict[str, Any]
    max_latency_ms: int
