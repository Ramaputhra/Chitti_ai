from desktop.brain.reasoning.models import ReasoningHypothesis
import uuid

class HypothesisValidator:
    def generate_hypothesis(self, query: str, results: list) -> ReasoningHypothesis:
        supporting = [r for r in results if getattr(r, "rejected", False) == False]
        contradicting = [r for r in results if getattr(r, "rejected", False) == True]
        
        return ReasoningHypothesis(
            hypothesis_id=str(uuid.uuid4()),
            premise=query,
            supporting_intelligence_results=supporting,
            contradicting_intelligence_results=contradicting
        )
