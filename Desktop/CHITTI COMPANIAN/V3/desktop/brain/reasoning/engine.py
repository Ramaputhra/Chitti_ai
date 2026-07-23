import uuid
import time
from desktop.brain.reasoning.models import (
    CognitiveConclusion, ReasoningTrace, ReasoningSession, ReasoningBudgetExceededException
)
from desktop.brain.reasoning.evaluator import EvidenceEvaluator
from desktop.brain.reasoning.conflict import ConflictResolutionEngine
from desktop.brain.reasoning.hypothesis import HypothesisValidator
from desktop.brain.reasoning.goal import GoalReasoner
from desktop.brain.reasoning.causal import CausalReasoner
from desktop.brain.reasoning.propagation import ConfidencePropagationEngine
from desktop.brain.reasoning.registry import ReasoningRuleRegistry

class ReasoningEngine:
    def __init__(self):
        self.registry = ReasoningRuleRegistry()
        self.evaluator = EvidenceEvaluator()
        self.conflict_engine = ConflictResolutionEngine(self.registry)
        self.hypothesis_validator = HypothesisValidator()
        self.goal_reasoner = GoalReasoner()
        self.causal_reasoner = CausalReasoner()
        self.propagation_engine = ConfidencePropagationEngine(self.registry)
        
    def reason(self, query: str, intelligence_results: list, budget_depth: int = 1) -> ReasoningSession:
        if budget_depth > 3:
            raise ReasoningBudgetExceededException("Maximum hypothesis depth (3) exceeded.")
            
        # 1. Hypothesis Generation
        hypothesis = self.hypothesis_validator.generate_hypothesis(query, intelligence_results)
        
        # 2. Conflict Resolution
        winning_results, resolutions = self.conflict_engine.resolve(
            hypothesis.supporting_intelligence_results, 
            hypothesis.contradicting_intelligence_results
        )
        
        # 3. Confidence Propagation
        final_conf, conf_log = self.propagation_engine.propagate(winning_results)
        
        # 4. Generate Conclusion
        trace = ReasoningTrace(
            intelligence_result_ids=["mock_res_1"],
            applied_reasoning_rules=["EPISTEMIC_OVER_EMPIRICAL", "INDEPENDENT_SOURCE_BOOST"]
        )
        
        assertion = "Action Approved" if hypothesis.supporting_intelligence_results == winning_results else "Action Rejected"
        if not winning_results:
            assertion = "Indeterminate"
            
        conclusion = CognitiveConclusion(
            conclusion_id=str(uuid.uuid4()),
            assertion=assertion,
            confidence=final_conf,
            evidence_trace=trace
        )
        
        # 5. Return immutable Session
        return ReasoningSession(
            session_id=str(uuid.uuid4()),
            incoming_query=query,
            hypotheses=[hypothesis],
            evidence_collection=intelligence_results,
            conflict_resolutions=resolutions,
            confidence_propagation_log=conf_log,
            final_conclusion=conclusion,
            complete_reasoning_trace=trace
        )
