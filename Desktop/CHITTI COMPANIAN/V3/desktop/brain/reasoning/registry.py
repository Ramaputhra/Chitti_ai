class ReasoningRuleRegistry:
    def __init__(self):
        self.precedence_rules = {"EPISTEMIC_OVER_EMPIRICAL": True}
        self.conflict_rules = {"DEPTH_TIE_BREAKER": True}
        self.confidence_rules = {"INDEPENDENT_SOURCE_BOOST": 0.1, "DECAY_PENALTY": -0.05}
        self.causal_rules = {"MAX_TRAVERSAL": 5}
        
    def get_rule(self, category: str, name: str):
        if category == "confidence":
            return self.confidence_rules.get(name)
        return True
