from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass(frozen=True)
class DecisionTrace:
    cognitive_conclusion_ids: List[str]
    applied_policies: List[str]

@dataclass(frozen=True)
class DecisionOutcome:
    outcome_id: str
    selected_intent: str
    decision_confidence: float
    risk_level: str
    priority_score: int
    evidence_trace: DecisionTrace

@dataclass(frozen=True)
class DecisionCandidate:
    candidate_id: str
    proposed_intent: str
    supporting_conclusions: List[Any]

@dataclass(frozen=True)
class DecisionSession:
    session_id: str
    candidates_evaluated: List[DecisionCandidate]
    policy_evaluations: List[str]
    priority_rankings: Dict[str, int]
    risk_assessments: Dict[str, str]
    final_outcome: DecisionOutcome
    timestamp: float = field(default_factory=time.time)

class DecisionBudgetExceededException(Exception):
    pass

class InvalidDecisionStateException(Exception):
    pass
