from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from desktop.product.assistants.base import Evidence

@dataclass
class KnowledgeTarget:
    """What needs documenting?"""
    kind: str # Python Function, Architecture, ADR, API, etc.
    identifier: str
    scope: str
    location: str

@dataclass
class KnowledgeDebt:
    """Discrepancies between intent, code, and documentation."""
    type: str # Missing, Stale, Architectural Drift, Broken Example, Contradictory, etc.
    severity: str # High, Medium, Low
    evidence: List[Evidence]
    confidence: float
    recommended_action: str

@dataclass
class KnowledgeCoverage:
    """Quantifies how well a component is documented."""
    component: str
    architecture_score: float
    api_docs_score: float
    examples_score: float
    tutorials_score: float
    adr_score: float
    overall_score: float

@dataclass
class AudienceProfile:
    """Who is the documentation for?"""
    experience: str # Beginner, Contributor, Architect
    role: str
    goal: str
    preferred_depth: str
    terminology: str
    examples_required: bool

@dataclass
class DocumentationPatch:
    """Reviewable artifact representing a documentation diff."""
    target: KnowledgeTarget
    before: str
    after: str
    reason: str
    confidence: float
    supporting_evidence: List[Evidence] # Rule 150 Explainability
    review_summary: str # One-sentence explanation for UI

@dataclass
class DecisionTrace:
    """Recovering the 'Why' behind architectural changes."""
    decision: str
    motivation: str
    alternatives_considered: List[str]
    tradeoffs: List[str]
    affected_components: List[str]
    origin_sprint: str
    origin_rule: str
    timestamp: datetime
    supporting_sources: List[str] # IDs from KnowledgeSource
    superseded_by: Optional[str] = None
