from dataclasses import dataclass
from typing import List

@dataclass
class CognitiveArtifact:
    artifact_id: str
    source_evidence_ids: List[str]

@dataclass
class LearnedRule(CognitiveArtifact):
    directive: str
    state: str
    confidence: float

@dataclass
class Habit(CognitiveArtifact):
    trigger_context: str
    expected_action_sequence: List[str]
    occurrence_count: int

@dataclass
class LearnedConcept(CognitiveArtifact):
    semantic_label: str
    associated_graph_nodes: List[str]

@dataclass
class ConsolidatedMemory(CognitiveArtifact):
    semantic_summary: str
    confidence_score: float

@dataclass
class Pattern(CognitiveArtifact):
    pattern_type: str
    involved_node_ids: List[str]
    frequency: int
    confidence: float
