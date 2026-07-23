from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass(frozen=True)
class ReasoningTrace:
    intelligence_result_ids: List[str]
    applied_reasoning_rules: List[str]

@dataclass(frozen=True)
class CognitiveConclusion:
    conclusion_id: str
    assertion: str
    confidence: float
    evidence_trace: ReasoningTrace

@dataclass(frozen=True)
class ReasoningHypothesis:
    hypothesis_id: str
    premise: str
    supporting_intelligence_results: List[Any]
    contradicting_intelligence_results: List[Any]

@dataclass(frozen=True)
class ReasoningSession:
    session_id: str
    incoming_query: str
    hypotheses: List[ReasoningHypothesis]
    evidence_collection: List[Any]
    conflict_resolutions: List[str]
    confidence_propagation_log: List[str]
    final_conclusion: CognitiveConclusion
    complete_reasoning_trace: ReasoningTrace
    timestamp: float = field(default_factory=time.time)

class ReasoningBudgetExceededException(Exception):
    pass
