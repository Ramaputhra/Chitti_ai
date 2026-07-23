class CapabilityRegistry:
    def __init__(self):
        self._capabilities = {}
        
    def register_capability(self, intent: str, template: dict):
        self._capabilities[intent.lower()] = template
        
    def get_template(self, intent: str) -> dict:
        return self._capabilities.get(intent.lower(), None)
