class EvidenceEvaluator:
    def evaluate_depth(self, intelligence_result) -> int:
        if hasattr(intelligence_result, "trace") and hasattr(intelligence_result.trace, "root_episodes"):
            return len(intelligence_result.trace.root_episodes)
        return 1
