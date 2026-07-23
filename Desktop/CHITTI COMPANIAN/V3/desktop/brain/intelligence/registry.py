class IntelligenceRegistry:
    def __init__(self):
        self.orchestrator = None
        
    def register_orchestrator(self, orchestrator):
        self.orchestrator = orchestrator
        
    def get_orchestrator(self):
        return self.orchestrator
