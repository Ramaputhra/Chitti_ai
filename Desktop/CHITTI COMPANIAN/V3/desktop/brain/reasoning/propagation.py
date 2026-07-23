class ConfidencePropagationEngine:
    def __init__(self, registry):
        self.registry = registry
        
    def propagate(self, winning_results: list) -> tuple:
        if not winning_results:
            return 0.0, ["Zero confidence due to lack of evidence"]
            
        base_conf = max([getattr(r, "confidence_score", 0.0) for r in winning_results])
        boost = self.registry.get_rule("confidence", "INDEPENDENT_SOURCE_BOOST") if len(winning_results) > 1 else 0.0
        decay = self.registry.get_rule("confidence", "DECAY_PENALTY")
        
        final_conf = max(0.0, min(1.0, base_conf + boost + decay))
        log = [f"Base: {base_conf}, Boost: {boost}, Decay: {decay}"]
        return final_conf, log
