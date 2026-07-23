from desktop.brain.intelligence.models import IntelligenceResult, ExplainabilityTrace, IntelligenceQuery

class DecisionIntelligenceService:
    def evaluate(self, query: IntelligenceQuery, artifacts, graph) -> IntelligenceResult:
        # Deterministic constraint checking (veto power)
        if "CEO" in query.active_context.get("target", ""):
            trace = ExplainabilityTrace(contributing_artifacts=["Rule_09"], root_episodes=["ep_112"])
            return IntelligenceResult("Constraint Violation: Formal tone required for CEO.", 1.0, trace, rejected=True)
        return IntelligenceResult("Action constraint check passed", 1.0, ExplainabilityTrace())

class RecommendationIntelligenceService:
    def evaluate(self, query: IntelligenceQuery, artifacts, graph) -> IntelligenceResult:
        trace = ExplainabilityTrace(contributing_artifacts=["Pattern_04"], root_episodes=["ep_302"])
        return IntelligenceResult("Suggestion: Start daily review", 0.7, trace)
