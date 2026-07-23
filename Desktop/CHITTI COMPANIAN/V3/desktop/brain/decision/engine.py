import uuid
import time
from desktop.brain.decision.models import (
    DecisionCandidate, DecisionOutcome, DecisionTrace, DecisionSession,
    DecisionBudgetExceededException, InvalidDecisionStateException
)
from desktop.brain.decision.policy import DecisionPolicyEngine
from desktop.brain.decision.priority import PriorityEvaluationEngine
from desktop.brain.decision.risk import RiskEvaluationEngine
from desktop.brain.decision.confidence import DecisionConfidenceModel
from desktop.brain.decision.validator import DecisionValidator
from desktop.brain.decision.registry import DecisionPolicyRegistry

class DecisionEngine:
    def __init__(self):
        self.registry = DecisionPolicyRegistry()
        self.registry.register_policy("safety", "never_execute_mechanics")
        
        self.policy_engine = DecisionPolicyEngine(self.registry)
        self.priority_engine = PriorityEvaluationEngine()
        self.risk_engine = RiskEvaluationEngine()
        self.confidence_model = DecisionConfidenceModel()
        self.validator = DecisionValidator()
        
    def decide(self, candidates: list) -> DecisionSession:
        max_candidates = 20
        max_policy = 100
        max_priority = 50
        max_risk = 20
        max_val = 1
        
        if len(candidates) > max_candidates:
            raise DecisionBudgetExceededException(f"Candidate count ({len(candidates)}) exceeds budget ({max_candidates}).")
            
        policy_logs = []
        rankings = {}
        risks = {}
        
        valid_candidates = []
        
        for c in candidates:
            max_policy -= 1
            if self.policy_engine.evaluate(c, max_policy):
                valid_candidates.append(c)
                policy_logs.append(f"{c.candidate_id}: PASSED")
            else:
                policy_logs.append(f"{c.candidate_id}: REJECTED")
                
        if not valid_candidates:
            return self._build_abort_session(candidates, policy_logs, rankings, risks)
            
        for c in valid_candidates:
            max_risk -= 1
            max_priority -= 1
            risks[c.candidate_id] = self.risk_engine.evaluate(c, max_risk)
            rankings[c.candidate_id] = self.priority_engine.evaluate(c, max_priority)
            
        selected = max(valid_candidates, key=lambda c: rankings[c.candidate_id])
        selected_risk = risks[selected.candidate_id]
        selected_priority = rankings[selected.candidate_id]
        selected_conf = self.confidence_model.calculate(selected_priority, selected_risk)
        
        trace = DecisionTrace(
            cognitive_conclusion_ids=["mock_conclusion"],
            applied_policies=["never_execute_mechanics"]
        )
        
        outcome = DecisionOutcome(
            outcome_id=str(uuid.uuid4()),
            selected_intent=selected.proposed_intent,
            decision_confidence=selected_conf,
            risk_level=selected_risk,
            priority_score=selected_priority,
            evidence_trace=trace
        )
        
        self.validator.validate_outcome(outcome, max_val)
        max_val -= 1
        
        return DecisionSession(
            session_id=str(uuid.uuid4()),
            candidates_evaluated=candidates,
            policy_evaluations=policy_logs,
            priority_rankings=rankings,
            risk_assessments=risks,
            final_outcome=outcome
        )
        
    def _build_abort_session(self, candidates, policy_logs, rankings, risks):
        outcome = DecisionOutcome(
            outcome_id=str(uuid.uuid4()),
            selected_intent="ABORT_EXHAUSTION",
            decision_confidence=0.0,
            risk_level="UNKNOWN",
            priority_score=0,
            evidence_trace=DecisionTrace([], [])
        )
        return DecisionSession(
            session_id=str(uuid.uuid4()),
            candidates_evaluated=candidates,
            policy_evaluations=policy_logs,
            priority_rankings=rankings,
            risk_assessments=risks,
            final_outcome=outcome
        )
