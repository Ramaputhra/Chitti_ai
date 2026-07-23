from typing import Dict, Any, List
from desktop.models.reasoning import ReasoningPlan, DecisionTrace, ReasoningStrategy, ReasoningCapabilityProfile, ReasoningMode

class PlanBuilder:
    """
    Constructs the final ReasoningPlan after all engines have made their decisions.
    """
    
    def build(self, decisions: Dict[str, Any], traces: List[DecisionTrace], elapsed_ms: int) -> ReasoningPlan:
        # Determine overall strategy based on combinations of decisions
        strategy = self._determine_strategy(decisions)
        
        # Determine capability profile
        profile = ReasoningCapabilityProfile(reasoning_mode=ReasoningMode.LOCAL_RULES)
        if decisions.get("requires_ai", False):
            profile.reasoning_mode = ReasoningMode.REMOTE_MODEL  # Or LOCAL_MODEL based on settings
            
        plan = ReasoningPlan(
            strategy=strategy,
            capability_profile=profile,
            requires_retrieval=decisions.get("requires_retrieval", False),
            requires_ai=decisions.get("requires_ai", False),
            requires_presentation=decisions.get("requires_presentation", False),
            requires_execution=decisions.get("requires_execution", False),
            requires_confirmation=decisions.get("requires_confirmation", False),
            requires_authentication=decisions.get("requires_authentication", False),
            preferred_services=decisions.get("preferred_services", []),
            confidence=self._calculate_overall_confidence(traces),
            reasoning_trace=traces,
            decision_time_ms=elapsed_ms
        )
        return plan

    def _determine_strategy(self, decisions: Dict[str, Any]) -> ReasoningStrategy:
        if decisions.get("requires_ai") and decisions.get("requires_retrieval"):
            return ReasoningStrategy.HYBRID
        elif decisions.get("requires_ai"):
            return ReasoningStrategy.AI_ASSISTED
        elif decisions.get("requires_retrieval"):
            return ReasoningStrategy.KNOWLEDGE
        elif decisions.get("requires_presentation") and not decisions.get("requires_execution"):
            return ReasoningStrategy.PRESENTATION
        elif decisions.get("requires_execution"):
            return ReasoningStrategy.EXECUTION
            
        return ReasoningStrategy.DIRECT

    def _calculate_overall_confidence(self, traces: List[DecisionTrace]) -> float:
        if not traces:
            return 1.0
        # Simple average of trace confidences
        total = sum(t.confidence for t in traces)
        return round(total / len(traces), 2)
