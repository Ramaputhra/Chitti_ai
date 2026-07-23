class CapabilityExecutionRegistry:
    def __init__(self):
        self._handlers = {}
        
    def register_handler(self, action_type: str, handler_func):
        self._handlers[action_type.upper()] = handler_func
        
    def get_handler(self, action_type: str):
        return self._handlers.get(action_type.upper())
