class ConflictResolutionEngine:
    def __init__(self, registry):
        self.registry = registry

    def resolve(self, supporting_results, contradicting_results):
        resolutions = []
        if contradicting_results and self.registry.get_rule("precedence", "EPISTEMIC_OVER_EMPIRICAL"):
            resolutions.append("Contradiction overridden via Epistemic Rule.")
            return contradicting_results, resolutions
        return supporting_results, resolutions
