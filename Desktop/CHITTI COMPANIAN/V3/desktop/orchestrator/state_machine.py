class RuntimeLifecycleState:
    BOOTING = "BOOTING"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    RESPONDING = "RESPONDING"
    
    ERROR = "ERROR"
    DEGRADED = "DEGRADED"
    SHUTDOWN = "SHUTDOWN"

class InvalidStateTransitionException(Exception):
    pass

class RuntimeStateMachine:
    def __init__(self):
        self._state = RuntimeLifecycleState.BOOTING
        
    @property
    def current_state(self):
        return self._state
        
    def transition(self, new_state: str):
        valid_transitions = {
            RuntimeLifecycleState.BOOTING: [RuntimeLifecycleState.INITIALIZING, RuntimeLifecycleState.ERROR],
            RuntimeLifecycleState.INITIALIZING: [RuntimeLifecycleState.READY, RuntimeLifecycleState.ERROR],
            RuntimeLifecycleState.READY: [RuntimeLifecycleState.LISTENING, RuntimeLifecycleState.SHUTDOWN],
            RuntimeLifecycleState.LISTENING: [RuntimeLifecycleState.PROCESSING, RuntimeLifecycleState.READY, RuntimeLifecycleState.SHUTDOWN],
            RuntimeLifecycleState.PROCESSING: [RuntimeLifecycleState.RESPONDING, RuntimeLifecycleState.ERROR],
            RuntimeLifecycleState.RESPONDING: [RuntimeLifecycleState.READY, RuntimeLifecycleState.LISTENING, RuntimeLifecycleState.ERROR],
            RuntimeLifecycleState.ERROR: [RuntimeLifecycleState.DEGRADED, RuntimeLifecycleState.READY, RuntimeLifecycleState.SHUTDOWN],
            RuntimeLifecycleState.DEGRADED: [RuntimeLifecycleState.READY, RuntimeLifecycleState.SHUTDOWN],
            RuntimeLifecycleState.SHUTDOWN: []
        }
        
        if new_state not in valid_transitions.get(self._state, []):
            raise InvalidStateTransitionException(f"Cannot transition from {self._state} to {new_state}")
            
        self._state = new_state

class PipelineEventBus:
    def __init__(self):
        self._subscribers = []
        
    def subscribe(self, callback):
        self._subscribers.append(callback)
        
    def publish(self, event_name: str, payload: dict = None):
        for sub in self._subscribers:
            sub(event_name, payload or {})
